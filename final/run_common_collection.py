"""Collect real predictions and GPU measurements, without API/judge or fabricated quality scores."""
import argparse,gc,hashlib,importlib.metadata,json,os,platform,random,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
os.environ.setdefault('USE_TF','0');os.environ.setdefault('ANONYMIZED_TELEMETRY','False')
from final.common_harness import load_common,infer,evaluate
from final.collection_profiles import SETTINGS,PROFILES,build_profile,warmup
from final.prepare_eval_final import canonical_hash
from final.config import MODELS


def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def error_frames(exc):
    """Code locations only; no exception body, source text, private paths or locals."""
    result=[]
    for frame in traceback.extract_tb(exc.__traceback__)[-8:]:
        path=Path(frame.filename).resolve()
        name=str(path.relative_to(ROOT)).replace('\\','/') if path.is_relative_to(ROOT) else path.name
        result.append({'file':name,'line':frame.lineno,'function':frame.name})
    return result


class CudaMeter:
    def __init__(self,torch):self.torch=torch
    def start(self):
        self.torch.cuda.synchronize();self.torch.cuda.reset_peak_memory_stats();self.started=time.perf_counter()
    def finish(self):
        self.torch.cuda.synchronize()
        return {'wall_seconds':time.perf_counter()-self.started,
                'peak_cuda_allocated_bytes':self.torch.cuda.max_memory_allocated(),
                'peak_cuda_reserved_bytes':self.torch.cuda.max_memory_reserved()}


def collect(inputs,system,meter,folder,root=ROOT,observer=None):
    """Only inference inputs go to system; failures remain in the complete denominator."""
    rows=[];folder=Path(folder)
    if len({item['id'] for item in inputs})!=len(inputs):raise ValueError('Duplicate input ID')
    with (folder/'predictions.jsonl').open('x',encoding='utf-8') as stream:
        for item in inputs:
            print('Collect:',folder.name,item['id'],flush=True)
            meter.start()
            row=infer([item],system,root=root)[0]
            measurement_error=None
            try:row.update(meter.finish())
            except Exception as exc:
                measurement_error=type(exc).__name__
                row.update(wall_seconds=None,peak_cuda_allocated_bytes=None,peak_cuda_reserved_bytes=None,
                           measurement_error_type=measurement_error)
            rows.append(row);stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
            if observer:observer(row)
            # CUDA errors may poison the process; do not claim usable later measurements.
            if measurement_error or row['system_error_type'] in {'OutOfMemoryError','AcceleratorError'}:
                raise RuntimeError('Fatal CUDA failure; partial rows retained')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-wandb',action='store_true');args=parser.parse_args()
    if args.output.exists():parser.error('Use a new output directory; do not overwrite evidence')
    args.output.mkdir(parents=True)
    meta={'status':'started','purpose':'generation_and_measurements_only','judge_used':False,
          'judge_validated_for_final':False,'quality_accepted':False,'efficiency_accepted':False,
          'started_utc':datetime.now(timezone.utc).isoformat(),'profiles_completed':[],'wandb_status':'disabled'}
    wb=None;generator=vision=system=None
    save=lambda:write_json(args.output/'metadata.json',meta)
    def stage(label):
        meta['stage']=label;save();print('Stage:',label,flush=True)
    save()
    try:
        stage('validate_inputs_and_rules')
        # Hashes checked before model loading. References only reach post-inference diagnostics.
        inputs,references,pack=load_common()
        domain_rules=json.loads((ROOT/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
        from final.comparison_recovery import verify
        meta['recovery']=verify(ROOT,SETTINGS,pack,domain_rules)
        write_json(args.output/'domain_protocol_v1.json',domain_rules)
        meta['domain_rules_sha256']=canonical_hash(domain_rules)
        meta['semantic_execution_status']='pending_validated_judge_and_documented_semantic_audit'
        stage('gpu_and_package_preflight')
        import torch,numpy as np
        if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):raise RuntimeError('A fresh Colab T4 is required')
        if importlib.metadata.version('bitsandbytes')!='0.50.2':raise RuntimeError('Pinned bitsandbytes required')
        from sqlite_support import ensure_sqlite
        sqlite=ensure_sqlite()
        properties=torch.cuda.get_device_properties(0)
        meta.update(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            python=platform.python_version(),packages={p:importlib.metadata.version(p) for p in
                ['torch','transformers','accelerate','bitsandbytes','sentence-transformers','chromadb','numpy','pillow','wandb']},
            sqlite=sqlite,hardware={'gpu':torch.cuda.get_device_name(0),'total_memory_bytes':properties.total_memory,
                'compute_capability':list(torch.cuda.get_device_capability(0)),'cuda':torch.version.cuda},
            models=MODELS,collection_settings=SETTINGS,collection_settings_sha256=canonical_hash(SETTINGS),
            inputs_sha256=pack['inputs_canonical_sha256'],references_sha256=pack['references_canonical_sha256'],
            source_hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                for parent in ['final','m3'] for p in (ROOT/parent).glob('*.py')})
        corpus=ROOT/'m3/corpus/documents.jsonl'
        meta['corpus_sha256']=hashlib.sha256(corpus.read_bytes()).hexdigest()
        if meta['corpus_sha256']!='7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505':raise ValueError('Corpus snapshot changed')
        documents=[json.loads(s) for s in corpus.read_text(encoding='utf-8').splitlines()]
        write_json(args.output/'collection_settings.json',SETTINGS);write_json(args.output/'input_manifest.json',inputs)
        stage('wandb_connection')
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='common-generation-collection',
                    config={'commit':meta['git_commit'],'collection':SETTINGS['version'],'judge_used':False},
                    settings=wandb.Settings(disable_git=True,disable_code=True,disable_job_creation=True,x_disable_stats=True,init_timeout=30))
                meta.update(wandb_status='connected',wandb_url=wb.url,wandb_run_id=wb.id)
            except Exception:meta['wandb_status']='connection_error'
        if args.require_wandb and wb is None:raise RuntimeError('W&B unavailable before loading models')
        save()
        # Real quantization kernel probe, before the measured profiles; never silently fall back.
        stage('nf4_kernel_preflight')
        import bitsandbytes as bnb
        probe=bnb.nn.Linear4bit(16,16,bias=False,compute_dtype=torch.float16,compress_statistics=True,quant_type='nf4').to('cuda')
        with torch.inference_mode():probe_result=probe(torch.ones((1,16),device='cuda',dtype=torch.float16))
        torch.cuda.synchronize()
        if not torch.isfinite(probe_result).all().item():raise RuntimeError('NF4 probe nonfinite')
        del probe,probe_result;gc.collect();torch.cuda.empty_cache();meta['nf4_kernel_probe_passed']=True
        stage('cpu_retrieval_and_reranker_setup')
        from rag_basic import DenseRetriever
        from ingest import chunk_documents
        from sentence_transformers import CrossEncoder
        from huggingface_hub import snapshot_download
        dense=DenseRetriever(chunk_documents(documents,220,30),*MODELS['embedding'],include_identity=True)
        local=snapshot_download(MODELS['reranker'][0],revision=MODELS['reranker'][1],allow_patterns=[
            'config.json','model.safetensors','pytorch_model.bin','tokenizer.json','tokenizer_config.json',
            'special_tokens_map.json','sentencepiece.bpe.model','vocab.*','merges.txt'])
        scorer=CrossEncoder(local,max_length=512,device='cpu')
        scorecards=[]
        for name in PROFILES:
            random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42)
            folder=args.output/name;folder.mkdir()
            stage(name+':loading')
            started=time.perf_counter()
            system,generator,vision=build_profile(name,documents,dense,scorer)
            torch.cuda.synchronize()
            info={'profile':name,'loading_seconds':time.perf_counter()-started,'generator':generator.load_settings,
                  'vlm_loaded':vision is not None,'classifier_loaded':False,'case_count_expected':len(inputs)}
            write_json(folder/'profile.json',info)
            stage(name+':warmup')
            write_json(folder/'warmup_excluded.json',warmup(system,folder));torch.cuda.synchronize()
            def observer(row):
                if wb:
                    try:wb.log({name+'/latency_seconds':row['wall_seconds'],name+'/peak_cuda_allocated_bytes':row['peak_cuda_allocated_bytes'],
                        name+'/system_error':int(row['system_error_type'] is not None),name+'/vision_used':int(bool(row['record'].get('components',{}).get('vision'))),
                        name+'/tool_used':int(bool(row['record'].get('tool_trace')))})
                    except Exception:meta['wandb_status']='logging_error'
            stage(name+':collect')
            rows=collect(inputs,system,CudaMeter(torch),folder,observer=observer)
            stage(name+':automatic_diagnostics_no_judge')
            details,summary=evaluate(rows,references,judge=None)
            summary.update(profile=name,peak_cuda_allocated_bytes=max(r['peak_cuda_allocated_bytes'] for r in rows),
                peak_cuda_reserved_bytes=max(r['peak_cuda_reserved_bytes'] for r in rows),
                collection_settings_sha256=meta['collection_settings_sha256'])
            summary['by_modality']={}
            for modality in ['text','image']:
                subset=[r for r in references if r['input_modality']==modality]
                ids={r['id'] for r in subset}
                _,separate=evaluate([r for r in rows if r['id'] in ids],subset,judge=None)
                summary['by_modality'][modality]=separate
            write_json(folder/'automatic_details.json',details);write_json(folder/'scorecard_candidate.json',summary)
            scorecards.append(summary);write_json(args.output/'scorecards_candidate.json',scorecards)
            meta['profiles_completed'].append(name);save()
            del system;system=None
            if vision is not None:vision.close();vision=None
            generator.close();generator=None;gc.collect();torch.cuda.empty_cache();torch.cuda.synchronize()
        meta['status']='collection_completed_semantic_evaluation_pending'
    except Exception as exc:
        meta.update(status='failed_partial_evidence_retained',error_type=type(exc).__name__,error_frames=error_frames(exc))
        print('Stopped; exception type:',type(exc).__name__,flush=True)
    finally:
        if wb:
            try:
                wb.summary['execution_status']=meta['status'];wb.summary['quality_accepted']=False;wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,ensure_ascii=False,indent=2))
    if meta['status'].startswith('failed'):sys.exit(1)


if __name__=='__main__':main()
