"""Second-family judge regression only; never declares final validation from familiar anchors."""
import argparse
from datetime import datetime,timezone
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('USE_TF','0')
from final.calibration_final import cases,schedule,verbose,summarize
from final.prepare_eval_final import canonical_hash
from final.run_judge_calibration import verify_review
from final.judge_final import FinalJudge,rubric_fingerprint


def verify_second_config(config,reference):
    if config['model']!='mistralai/Mistral-7B-Instruct-v0.3' or config['revision']!='c170c708c41dac9275d15a8fff4eca08d52bab71':
        raise ValueError('Unexpected second candidate checkpoint')
    for key in ['precision','compute_dtype','double_quantization','bitsandbytes_version','max_new_tokens','seed','rubric_version']:
        if config[key]!=reference[key]:raise ValueError('Uncontrolled change in '+key)
    if config['rubric_changed_from_qwen_calibration'] or config['acceptance_rules_changed']:
        raise ValueError('Regression rules must not be relaxed')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-wandb',action='store_true')
    args=parser.parse_args()
    if args.output.exists():parser.error('Use a new output directory')
    args.output.mkdir(parents=True)
    meta={'status':'started','purpose':'second_family_judge_regression_not_final_validation',
          'started_utc':datetime.now(timezone.utc).isoformat(),'wandb_status':'disabled',
          'regression_gate_passed':False,'confirmation_executed':False,'judge_validated_for_final':False,
          'final_gold_loaded':False,'score_adjusted':False,'human_semantic_audit_required':True}
    generator=wb=None
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        # Existing approval authenticates the unchanged examples/rubric, not a claim that the new model works.
        approval=verify_review(ROOT/'final/eval/calibration_review_v1')
        config=json.loads((ROOT/'final/judge_second_config.json').read_text(encoding='utf-8'))
        verify_second_config(config,json.loads((ROOT/'final/judge_calibration_config.json').read_text(encoding='utf-8')))
        failure=ROOT/'final/evidence/judge_calibration_01/original_results.zip'
        failure_hash=hashlib.sha256(failure.read_bytes()).hexdigest()
        if failure_hash!='b452ba5a7d558e58cad00d36168aa151ebb1e24be8d282b52efda04dbc8439ee':
            raise ValueError('Original rejected run changed')
        if config['rubric_version']!='final-judge-candidate-1.1' or config['rubric_changed_from_qwen_calibration']:
            raise ValueError('This regression must preserve the original rubric')
        meta.update(config=config,config_canonical_sha256=canonical_hash(config),
                    anchor_approval_canonical_sha256=canonical_hash(approval),rubric_sha256=rubric_fingerprint(),
                    original_rejected_archive_sha256=failure_hash,anchors_canonical_sha256=canonical_hash(cases()),
                    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in [ROOT/'final/run_second_judge.py',ROOT/'final/judge_final.py',ROOT/'final/calibration_final.py',
                                             ROOT/'final/generators.py',ROOT/'final/run_judge_calibration.py',ROOT/'m3/judge.py',
                                             ROOT/'m3/structured_output.py',ROOT/'m3/response_v4.py',ROOT/'m3/rag_basic.py']})
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='second-family-judge-regression',
                    config={'protocol':config['protocol'],'model':config['model'],'revision':config['revision'],'commit':meta['git_commit']},
                    settings=wandb.Settings(disable_git=True,disable_code=True,disable_job_creation=True,x_disable_stats=True,init_timeout=30))
                meta.update(wandb_status='connected',wandb_run_id=wb.id,wandb_url=wb.url)
            except Exception:meta['wandb_status']='connection_error'
        if args.require_wandb and wb is None:raise RuntimeError('W&B unavailable; verify notebook secret access, never print the key')
        import torch
        import numpy as np
        if not torch.cuda.is_available():raise RuntimeError('Enable a fresh Colab T4 session')
        if importlib.metadata.version('bitsandbytes')!=config['bitsandbytes_version']:
            raise RuntimeError('Unexpected bitsandbytes version')
        random.seed(config['seed']);np.random.seed(config['seed']);torch.manual_seed(config['seed']);torch.cuda.manual_seed_all(config['seed'])
        meta.update(gpu=torch.cuda.get_device_name(0),packages={n:importlib.metadata.version(n) for n in ['torch','transformers','accelerate','bitsandbytes','wandb']})
        import bitsandbytes as bnb
        probe=bnb.nn.Linear4bit(16,16,bias=False,compute_dtype=torch.float16,compress_statistics=True,quant_type='nf4').to('cuda')
        with torch.inference_mode():check=probe(torch.ones((1,16),device='cuda',dtype=torch.float16))
        torch.cuda.synchronize()
        if not torch.isfinite(check).all().item():raise RuntimeError('NF4 CUDA preflight failed')
        del probe,check
        torch.cuda.empty_cache()
        meta['nf4_cuda_kernel_preflight_passed']=True;save()
        from final.generators import CausalGenerator
        started=time.perf_counter()
        generator=CausalGenerator(config['model'],config['revision'],precision=config['precision'],max_new_tokens=config['max_new_tokens'])
        torch.cuda.synchronize()
        meta.update(load_seconds=time.perf_counter()-started,load_settings=generator.load_settings,
                    cuda_allocated_bytes=torch.cuda.memory_allocated(),cuda_reserved_bytes=torch.cuda.memory_reserved())
        save()
        by_id={c['id']:c for c in cases()};rows=[]
        with (args.output/'raw_judgements.jsonl').open('w',encoding='utf-8') as out:
            for condition,cid in schedule():
                print('Second judge:',condition,cid,flush=True)
                record=by_id[cid]['record']
                if condition.endswith('verbose'):record=verbose(record)
                result=FinalJudge(generator,mitigate_verbosity=not condition.startswith('before_')).evaluate(record)
                row={'condition':condition,'id':cid,'judgement':result}
                rows.append(row);out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
                if wb:
                    try:wb.log({'regression/latency_seconds':result['latency_seconds'],'regression/parsed':int(result['score'] is not None)})
                    except Exception:meta['wandb_status']='logging_error'
        summary=summarize(rows)
        (args.output/'regression_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        meta.update(regression_gate_passed=summary['gate_passed'],
                    status='completed_regression_passed_confirmation_pending' if summary['gate_passed'] else 'completed_regression_failed')
    except Exception as exc:
        meta.update(status='failed',error_type=type(exc).__name__)
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        if generator:
            try:generator.close()
            except Exception:meta['cleanup_error']=True
        if wb:
            try:
                wb.summary['execution_status']=meta['status']
                wb.summary['regression_gate_passed']=meta['regression_gate_passed']
                wb.summary['judge_validated_for_final']=False
                wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
