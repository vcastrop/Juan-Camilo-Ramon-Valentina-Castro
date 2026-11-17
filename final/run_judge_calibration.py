"""GPU judge calibration, gated by real human review of synthetic anchors."""
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
from final.calibration_final import cases,verbose,schedule,summarize,ACCEPTANCE
from final.prepare_eval_final import canonical_hash


def verify_review(pack):
    path=pack/'human_approval.json'
    if not path.exists():raise ValueError('Synthetic calibration anchors have not received human approval')
    approval=json.loads(path.read_text(encoding='utf-8'))
    if approval.get('status')!='approved' or set(approval.get('approved_ids',[]))!={c['id'] for c in cases()}:
        raise ValueError('Incomplete calibration approval')
    anchors=json.loads((pack/'anchors.json').read_text(encoding='utf-8'))
    rules=json.loads((pack/'rules.json').read_text(encoding='utf-8'))
    if canonical_hash(anchors)!=canonical_hash(cases()) or canonical_hash(rules)!=canonical_hash(ACCEPTANCE):
        raise ValueError('Code differs from reviewed calibration package')
    if approval.get('anchors_canonical_sha256')!=canonical_hash(anchors) or approval.get('rules_canonical_sha256')!=canonical_hash(rules):
        raise ValueError('Calibration package changed after approval')
    return approval


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--require-wandb',action='store_true')
    args=p.parse_args()
    if args.output.exists():p.error('Use a new output directory')
    args.output.mkdir(parents=True)
    meta={'status':'started','purpose':'synthetic_judge_calibration_not_system_scorecard',
          'started_utc':datetime.now(timezone.utc).isoformat(),'wandb_status':'disabled',
          'calibration_gate_passed':False,'human_review_of_judge_reasons':'pending','judge_validated_for_final':False,
          'final_gold_loaded':False,'score_adjusted':False}
    wb=generator=None
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        pack=ROOT/'final/eval/calibration_review_v1'
        try:approval=verify_review(pack)
        except ValueError:
            meta['status']='blocked_pending_human_review'
            raise
        config_path=ROOT/'final/judge_calibration_config.json'
        config=json.loads(config_path.read_text(encoding='utf-8'))
        meta.update(config=config,config_canonical_sha256=canonical_hash(config),
                    approval_canonical_sha256=canonical_hash(approval),anchors_canonical_sha256=canonical_hash(cases()),
                    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in [ROOT/'final/judge_final.py',ROOT/'final/calibration_final.py',ROOT/'final/generators.py',
                                             ROOT/'final/run_judge_calibration.py',ROOT/'m3/judge.py',ROOT/'m3/structured_output.py',ROOT/'m3/response_v4.py',ROOT/'m3/rag_basic.py']})
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='judge-calibration-final',
                    config={'protocol':config['protocol'],'model':config['model'],'revision':config['revision'],'commit':meta['git_commit']},
                    settings=wandb.Settings(disable_git=True,disable_code=True,disable_job_creation=True,x_disable_stats=True,init_timeout=30))
                meta.update(wandb_status='connected',wandb_run_id=wb.id,wandb_url=wb.url)
            except Exception:meta['wandb_status']='connection_error'
        if args.require_wandb and wb is None:raise RuntimeError('W&B unavailable; verify notebook secret access without printing the key')
        import torch
        import numpy as np
        if not torch.cuda.is_available():raise RuntimeError('Enable a fresh Colab T4 session')
        if importlib.metadata.version('bitsandbytes')!=config['bitsandbytes_version']:
            raise RuntimeError('bitsandbytes version differs from pinned calibration configuration')
        random.seed(config['seed']);np.random.seed(config['seed']);torch.manual_seed(config['seed']);torch.cuda.manual_seed_all(config['seed'])
        meta.update(gpu=torch.cuda.get_device_name(0),packages={n:importlib.metadata.version(n) for n in ['torch','transformers','accelerate','bitsandbytes','wandb']})
        from final.generators import CausalGenerator
        from final.judge_final import FinalJudge
        start=time.perf_counter()
        generator=CausalGenerator(config['model'],config['revision'],precision=config['precision'],max_new_tokens=config['max_new_tokens'])
        torch.cuda.synchronize()
        meta.update(load_seconds=time.perf_counter()-start,load_settings=generator.load_settings,
                    cuda_allocated_bytes=torch.cuda.memory_allocated(),cuda_reserved_bytes=torch.cuda.memory_reserved())
        save()
        by_id={c['id']:c for c in cases()};rows=[]
        with (args.output/'raw_judgements.jsonl').open('w',encoding='utf-8') as out:
            for condition,cid in schedule():
                print('Judge calibration:',condition,cid,flush=True)
                record=by_id[cid]['record']
                if condition.endswith('verbose'):record=verbose(record)
                judge=FinalJudge(generator,mitigate_verbosity=not condition.startswith('before_'))
                judgement=judge.evaluate(record)
                row={'condition':condition,'id':cid,'judgement':judgement}
                rows.append(row);out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
                if wb:
                    try:wb.log({'calibration/latency_seconds':judgement['latency_seconds'],
                                'calibration/parsed':int(judgement['score'] is not None)})
                    except Exception:meta['wandb_status']='logging_error'
        summary=summarize(rows)
        (args.output/'calibration_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        meta.update(calibration_gate_passed=summary['gate_passed'],
                    status='completed_gate_passed_pending_human_audit' if summary['gate_passed'] else 'completed_gate_failed')
    except Exception as exc:
        if meta['status']!='blocked_pending_human_review':meta['status']='failed'
        meta['error_type']=type(exc).__name__
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        if generator:
            try:generator.close()
            except Exception:meta['cleanup_error']=True
        if wb:
            try:
                wb.summary['execution_status']=meta['status']
                wb.summary['calibration_gate_passed']=meta['calibration_gate_passed']
                wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
