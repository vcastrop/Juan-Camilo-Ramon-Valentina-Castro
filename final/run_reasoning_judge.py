"""Reasoning judge pilot -> full known-case regression; confirmation remains separate."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import subprocess
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('USE_TF','0')
from final.calibration_final import cases,schedule,verbose
from final.reasoning_calibration import request_seed,pilot_summary,full_summary,validate_config
from final.judge_criteria import CriteriaJudge
from final.prepare_eval_final import canonical_hash
from final.run_judge_calibration import verify_review


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--require-wandb',action='store_true')
    args=p.parse_args()
    if args.output.exists():p.error('Use a new output directory')
    args.output.mkdir(parents=True)
    meta={'status':'started','purpose':'criteria_reasoning_judge_pilot_and_regression',
          'started_utc':datetime.now(timezone.utc).isoformat(),'wandb_status':'disabled',
          'pilot_passed':False,'regression_gate_passed':False,'confirmation_executed':False,
          'judge_validated_for_final':False,'final_gold_loaded':False,'score_adjusted':False,
          'private_thinking_text_retained':False,'human_semantic_audit_required':True}
    gen=wb=None;rows=[]
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        approval=verify_review(ROOT/'final/eval/calibration_review_v1')
        cfg=json.loads((ROOT/'final/judge_reasoning_config.json').read_text(encoding='utf-8'))
        validate_config(cfg)
        meta.update(config=cfg,config_canonical_sha256=canonical_hash(cfg),
                    legacy_anchor_approval_canonical_sha256=canonical_hash(approval),
                    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                        ROOT/'final/run_reasoning_judge.py',ROOT/'final/reasoning_generator.py',ROOT/'final/judge_criteria.py',
                        ROOT/'final/reasoning_calibration.py',ROOT/'final/generators.py',ROOT/'final/judge_final.py',
                        ROOT/'final/calibration_final.py',ROOT/'final/run_judge_calibration.py',ROOT/'final/prepare_eval_final.py',
                        ROOT/'m3/judge.py',ROOT/'m3/structured_output.py',ROOT/'m3/response_v4.py',ROOT/'m3/rag_basic.py']})
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='criteria-reasoning-judge',
                    config={'protocol':cfg['protocol'],'model':cfg['model'],'revision':cfg['revision'],'commit':meta['git_commit']},
                    settings=wandb.Settings(disable_git=True,disable_code=True,disable_job_creation=True,x_disable_stats=True,init_timeout=30))
                meta.update(wandb_status='connected',wandb_run_id=wb.id,wandb_url=wb.url)
            except Exception:meta['wandb_status']='connection_error'
        if args.require_wandb and wb is None:raise RuntimeError('W&B unavailable; enable notebook access to its secret without printing it')
        import torch
        if not torch.cuda.is_available():raise RuntimeError('Enable a fresh Colab T4 session')
        if importlib.metadata.version('bitsandbytes')!=cfg['bitsandbytes_version']:raise RuntimeError('Unexpected bitsandbytes version')
        meta.update(gpu=torch.cuda.get_device_name(0),packages={n:importlib.metadata.version(n) for n in ['torch','transformers','tokenizers','bitsandbytes','wandb']})
        # No weights before native tokenizer/boundary preflight.
        from transformers import AutoTokenizer
        from final.reasoning_generator import encode_reasoning_chat,ReasoningGenerator
        tokenizer=AutoTokenizer.from_pretrained(cfg['model'],revision=cfg['revision'],trust_remote_code=False)
        by_id={c['id']:c for c in cases()}
        from judge import evidence_payload
        for cid in cfg['pilot_ids']:
            encode_reasoning_chat(tokenizer,CriteriaJudge(None).system,json.dumps(evidence_payload(by_id[cid]['record']),ensure_ascii=False))
        boundary=tokenizer.convert_tokens_to_ids('</think>')
        if type(boundary) is not int or boundary==tokenizer.unk_token_id:raise RuntimeError('Missing native thinking boundary')
        meta['native_tokenizer_preflight_passed']=True;del tokenizer;save()
        started=time.perf_counter();gen=ReasoningGenerator(cfg);torch.cuda.synchronize()
        meta.update(load_seconds=time.perf_counter()-started,load_settings=gen.load_settings,cuda_allocated_bytes=torch.cuda.memory_allocated())
        stream=(args.output/'raw_judgements.jsonl').open('w',encoding='utf-8')
        try:
            def evaluate(condition,cid,pilot=False):
                print('Reasoning judge:',condition,cid,'pilot' if pilot else '',flush=True)
                record=by_id[cid]['record']
                if condition.endswith('verbose'):record=verbose(record)
                gen.set_request_seed(request_seed(cid,cfg['seed']))
                j=CriteriaJudge(gen,mitigate_verbosity=not condition.startswith('before_')).evaluate(record)
                row={'condition':condition,'id':cid,'pilot':pilot,'judgement':j}
                rows.append(row);stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
                if wb:
                    try:wb.log({'judge/latency_seconds':j['latency_seconds'],'judge/valid_final':int(j['score'] is not None)})
                    except Exception:meta['wandb_status']='logging_error'
            for cid in cfg['pilot_ids']:
                evaluate('main_mitigated',cid,pilot=True)
                partial=pilot_summary(rows,[r['id'] for r in rows])
                if cfg['pilot_fail_fast'] and not partial['pilot_passed']:break
            pilot=pilot_summary(rows,cfg['pilot_ids'])
            (args.output/'pilot_summary.json').write_text(json.dumps(pilot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            meta['pilot_passed']=pilot['pilot_passed']
            if not pilot['pilot_passed']:
                meta['status']='completed_pilot_failed'
            else:
                for condition,cid in schedule():
                    if condition=='main_mitigated' and cid in cfg['pilot_ids']:continue
                    evaluate(condition,cid)
                summary=full_summary(rows)
                (args.output/'regression_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                meta.update(regression_gate_passed=summary['gate_passed'],
                            status='completed_regression_passed_confirmation_pending' if summary['gate_passed'] else 'completed_regression_failed')
        finally:stream.close()
        meta['judgements_executed']=len(rows)
    except Exception as exc:
        meta.update(status='failed',error_type=type(exc).__name__)
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    finally:
        if gen:
            try:gen.close()
            except Exception:meta['cleanup_error']=True
        if wb:
            try:
                wb.summary['execution_status']=meta['status'];wb.summary['judge_validated_for_final']=False;wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
