"""Focused T4 correction probe, original fixtures retained; not final gold evaluation."""
import argparse
from datetime import datetime, timezone
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(ROOT/'m3')]
os.environ.setdefault('USE_TF','0')
os.environ.setdefault('ANONYMIZED_TELEMETRY','False')
from final.config import MODELS, SEED, VERSION


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('Choose a new output directory')
    args.output.mkdir(parents=True)
    meta = {'status':'started','purpose':'correction02_development_not_final_evaluation',
            'version':VERSION,'models':MODELS,'seed':SEED,'started_utc':datetime.now(timezone.utc).isoformat(),
            'quality_approved':False,'exceptions':[],'wandb_status':'disabled',
            'latency_policy':'component VLM separate, then cached-read orchestration; not fresh end-to-end multimodal latency'}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    save()
    rows, wb = [], None
    stream = (args.output/'correction_rows.jsonl').open('w',encoding='utf-8')
    def attempt(stage, case_id, fn):
        print(stage,case_id,flush=True)
        started = time.perf_counter()
        try:
            row = {'stage':stage,'case_id':case_id,'result':fn()}
        except Exception as exc:
            row = {'stage':stage,'case_id':case_id,'error':type(exc).__name__,'detail':str(exc)}
            meta['exceptions'].append({'stage':stage,'case_id':case_id,'error':type(exc).__name__})
        row['stage_wall_seconds'] = time.perf_counter()-started
        result = row.get('result',{})
        visual = result.get('visual')
        flags = {'exception_free':'error' not in row}
        if visual is not None:
            flags['visual_schema_valid'] = visual.get('parse_error') is None and isinstance(visual.get('output'),dict)
            flags['vision_model_used'] = bool(visual.get('vision_model_used'))
        if 'output' in result:
            flags['answer_schema_present'] = isinstance(result['output'],dict)
            flags['abstention'] = bool((result.get('output') or {}).get('abstencion'))
        row['technical_flags'] = flags
        rows.append(row)
        stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
        if wb:
            try:
                metrics = {stage+'/wall_seconds':row['stage_wall_seconds']}
                metrics.update({stage+'/'+k:int(v) for k,v in flags.items()})
                wb.log(metrics)
            except Exception:
                meta['wandb_status']='logging_error'
        return row
    try:
        from sqlite_support import ensure_sqlite
        meta['sqlite'] = ensure_sqlite()
        import torch
        import numpy as np
        from PIL import Image
        if not torch.cuda.is_available():
            raise RuntimeError('Enable Colab T4')
        random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED)
        meta.update(gpu=torch.cuda.get_device_name(0),
            git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            packages={name:importlib.metadata.version(name) for name in ['torch','transformers','pillow','wandb']},
            source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (ROOT/'final').glob('*.py')})
        archive = ROOT/'final/evidence/integration_01/original_results.zip'
        meta['original_archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
        assert meta['original_archive_sha256']=='4a1b1a2d3bfdfb21630863436dc0473635aea9711c16aa7d80fa33c976c29ca0'
        fixture_dir = args.output/'fixtures';fixture_dir.mkdir()
        with zipfile.ZipFile(archive) as z:
            fixtures = json.loads(z.read('fixture_manifest.json'))
            old_rows = [json.loads(s) for s in z.read('integration_rows.jsonl').decode().splitlines()]
            for case in fixtures:
                name = Path(case['path']).name
                raw = z.read('fixtures/'+name)
                assert hashlib.sha256(raw).hexdigest()==case['sha256']
                dest = fixture_dir/name;dest.write_bytes(raw);case['path']=str(dest)
        (args.output/'fixture_manifest.json').write_text(json.dumps(fixtures,indent=2,ensure_ascii=False),encoding='utf-8')
        from final.visual_fields import transcription_to_visual
        replay=[]
        for r in old_rows:
            if r['stage']=='visual_component':
                try:
                    obj,evidence=transcription_to_visual(r['result']['visual']['raw_response'])
                    replay.append({'case_id':r['case_id'],'output':obj,'field_evidence':evidence,'parse_error':None})
                except (ValueError,TypeError) as exc:
                    replay.append({'case_id':r['case_id'],'output':None,'parse_error':str(exc)})
        (args.output/'offline_replay.json').write_text(json.dumps({'purpose':'posthoc_parser_regression_not_new_inference','rows':replay},indent=2,ensure_ascii=False),encoding='utf-8')
        if os.getenv('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='correction02_development',
                    config={'version':VERSION,'phase':'development_only'},
                    settings=wandb.Settings(console='off',disable_git=True,disable_code=True,
                        disable_job_creation=True,x_disable_stats=True,init_timeout=20))
                meta.update(wandb_status='connected',wandb_run_id=wb.id)
            except Exception:
                meta['wandb_status']='connection_error'
        save()
        from final.adapters import Vision,AnswerAdapter
        from final.integration import IntegratedSystem
        print('Loading VLM first; uniform image handled by pixel guard...',flush=True)
        vision=Vision();reads={}
        for case in fixtures:
            r=attempt('visual_component',case['id'],lambda case=case:{'visual':vision.extract(Image.open(case['path']).convert('RGB'))})
            if 'result' in r:
                reads[case['id']]=r['result']['visual']
        vision.close();del vision;gc.collect();torch.cuda.empty_cache()
        from rag_basic import DenseRetriever
        from ingest import chunk_documents
        from sentence_transformers import CrossEncoder
        from huggingface_hub import snapshot_download
        docs=[json.loads(s) for s in (ROOT/'m3/corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        meta['corpus_sha256']=hashlib.sha256((ROOT/'m3/corpus/documents.jsonl').read_bytes()).hexdigest()
        assert meta['corpus_sha256']=='7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505'
        chunks=chunk_documents(docs,220,30)
        dense=DenseRetriever(chunks,*MODELS['embedding'],include_identity=True)
        local=snapshot_download(MODELS['reranker'][0],revision=MODELS['reranker'][1],
            allow_patterns=['config.json','model.safetensors','pytorch_model.bin','tokenizer.json','tokenizer_config.json',
                'special_tokens_map.json','sentencepiece.bpe.model','vocab.*','merges.txt'])
        scorer=CrossEncoder(local,max_length=512,device='cpu')
        print('Loading generator once for text and visual orchestration...',flush=True)
        answer=AnswerAdapter(docs,dense,scorer)
        system=IntegratedSystem(docs,answer)
        questions=['¿Qué modalidad registra CO1.PCCNTR.1180445?',
            '¿Cuál es la diferencia absoluta entre los valores de CO1.PCCNTR.1180445 y CO1.PCCNTR.1637043? Cita ambos.',
            '¿Qué concluyó la auditoría de ejecución física de CO1.PCCNTR.1637043?']
        for i,q in enumerate(questions):
            attempt('text',f'text_dev_{i}',lambda q=q:system.predict(q))
        for case in fixtures:
            if case['id'] not in reads:
                continue
            class SavedRead:
                def extract(self,image):
                    return reads[case['id']]
            multimodal=IntegratedSystem(docs,answer,vision=SavedRead())
            attempt('visual_orchestration_cached',case['id'],lambda case=case,s=multimodal:s.predict(
                case['question'],image=Image.open(case['path']).convert('RGB')))
        answer.close()
        meta.update(status='completed_pending_human_review',final_gold_loaded=False,classifier_repeated=False,
            visual_schema_valid=sum(r['technical_flags'].get('visual_schema_valid',False) for r in rows if r['stage']=='visual_component'),
            visual_cases=sum(r['stage']=='visual_component' for r in rows),
            vision_model_calls=sum(r['technical_flags'].get('vision_model_used',False) for r in rows if r['stage']=='visual_component'),
            uniform_pixel_guards=sum(r.get('result',{}).get('visual',{}).get('guard')=='uniform_pixels' for r in rows if r['stage']=='visual_component'),
            valid_model_reads=sum(r['technical_flags'].get('vision_model_used',False) and r['technical_flags'].get('visual_schema_valid',False) for r in rows if r['stage']=='visual_component'),
            schema_metric_is_not_accuracy=True)
        if meta['exceptions']:
            meta['status']='completed_with_case_errors'
        elif meta['visual_schema_valid'] < meta['visual_cases']:
            meta['status']='completed_with_visual_validation_errors'
    except Exception as exc:
        meta.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        stream.close()
        if wb:
            try:
                wb.summary['execution_status']=meta['status']
                wb.summary['exceptions']=len(meta['exceptions'])
                wb.summary['quality_approved']=False
                wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:
                meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,indent=2,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
