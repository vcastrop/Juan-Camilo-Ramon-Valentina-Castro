"""New synthetic API calibration only. No final gold, paid mode or model fallback."""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from final.calibration_final import cases,schedule,summarize,verbose
from final.hydrogen_judge_client import ApiFailure,validate_config
from final.hydrogen_resume import ResumableHydrogenGenerator as GeminiRESTGenerator,verify_checkpoint,register_resume,POLICY
from final.hydrogen_history import verify_history,register_hydrogen
from final.judge_final import FinalJudge,rubric_fingerprint
from final.prepare_eval_final import canonical_hash
from final.reasoning_calibration import request_seed
from final.run_judge_calibration import verify_review


def pilot_summary(rows,ids):
    anchors={c['id']:c for c in cases()};by_id={r['id']:r['judgement'] for r in rows}
    failed=[];invalid=[]
    for cid in ids:
        if cid in by_id:
            score=by_id[cid].get('score');low,high=anchors[cid]['expected_score_range']
            if type(score) is not int or not 1<=score<=5:invalid.append(cid)
            elif not low<=score<=high:failed.append(cid)
    complete=len(rows)==len(ids) and len(by_id)==len(ids) and set(by_id)==set(ids)
    return {'pilot_passed':complete and not failed and not invalid,'expected_cases':len(ids),'cases':len(rows),
            'failed_ids':failed,'invalid_ids':invalid,'unexecuted_ids':[cid for cid in ids if cid not in by_id],
            'judge_validated_for_final':False,'pilot_scores_reused_for_main':True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--budget-dir',type=Path,required=True)
    parser.add_argument('--confirm-free-project',action='store_true')
    parser.add_argument('--require-wandb',action='store_true')
    args=parser.parse_args()
    if args.output.exists():parser.error('Use a new result directory; do not overwrite evidence')
    args.output.mkdir(parents=True)
    (args.output/'resume_policy.json').write_text(json.dumps(POLICY,indent=2)+'\n',encoding='utf-8')
    meta={'status':'started','purpose':'synthetic_hydrogen_judge_checkpoint_continuation','started_utc':datetime.now(timezone.utc).isoformat(),
        'pilot_passed':False,'regression_gate_passed':False,'judge_validated_for_final':False,
        'final_gold_loaded':False,'confirmation_executed':False,'score_adjusted':False,
        'billing_mode':'free_project_attested_only','actual_invoice_verified':False,
        'thinking_text_retained':False,'wandb_status':'disabled'}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    wb=None;generator=None;rows=[]
    save()
    try:
        if not args.confirm_free_project:raise ApiFailure('confirm_project_has_no_billing_before_any_request')
        if not os.environ.get('GEMINI_API_KEY'):raise ApiFailure('missing_gemini_api_key')
        approval=verify_review(ROOT/'final/eval/calibration_review_v1')
        cfg=json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'));validate_config(cfg)
        checkpoint=verify_checkpoint(ROOT)
        rows=copy.deepcopy(checkpoint['saved_rows'])
        for saved in rows:
            saved['provenance']={'origin':'saved_hydrogen_09','archive_sha256':checkpoint['archive_sha256'],'regenerated':False}

        meta.update(checkpoint_archive_sha256=checkpoint['archive_sha256'],historical_generation_http_calls=4,historical_valid_judgements=1,reused_valid_judgements=1,resume_policy=POLICY,model_version_inherited_from_checkpoint=True,previous_reservations_retained=True)
        meta.update(config=cfg,config_canonical_sha256=canonical_hash(cfg),free_project_attested=True,
            approved_anchor_package_sha256=canonical_hash(approval),rubric_sha256=rubric_fingerprint(),
            git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in [
                'final/run_hydrogen_continuation.py','final/hydrogen_resume.py','final/run_hydrogen_calibration.py','final/hydrogen_judge_client.py','final/hydrogen_history.py','final/gemini_judge_client.py','final/api_budget.py','final/judge_final.py',
                'final/calibration_final.py','final/reasoning_calibration.py','final/run_judge_calibration.py',
                'final/prepare_eval_final.py','m3/judge.py','m3/structured_output.py']})
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb=wandb.init(entity='jcramonp-eanit',project='contractrisk-final',job_type='synthetic-api-judge',
                    config={'protocol':cfg['protocol'],'model':cfg['model'],'commit':meta['git_commit']},
                    settings=wandb.Settings(disable_git=True,disable_code=True,disable_job_creation=True,x_disable_stats=True,init_timeout=30))
                meta.update(wandb_status='connected',wandb_run_id=wb.id,wandb_url=wb.url)
            except Exception:meta['wandb_status']='connection_error'
        if args.require_wandb and wb is None:raise ApiFailure('wandb_unavailable_before_api_dispatch')
        generator=GeminiRESTGenerator(os.environ['GEMINI_API_KEY'],cfg,args.budget_dir/'api_budget_ledger.json',
            args.output/'api_requests.jsonl',confirmed_free_project=True,checkpoint=checkpoint)
        register_resume(args.budget_dir,cfg,checkpoint)
        meta['model_preflight']=generator.preflight();save()
        anchors={c['id']:c['record'] for c in cases()}
        with (args.output/'raw_judgements.jsonl').open('w',encoding='utf-8') as stream:
            for saved in rows:stream.write(json.dumps(saved,ensure_ascii=False)+'\n')
            stream.flush()
            done={(r['condition'],r['id']) for r in rows}

            def evaluate(condition,cid,pilot=False):
                print('API judge:',condition,cid,flush=True)
                record=anchors[cid]
                if condition.endswith('verbose'):record=verbose(record)
                generator.set_request_seed(request_seed(cid,cfg['seed']))
                judgement=FinalJudge(generator,mitigate_verbosity=not condition.startswith('before_')).evaluate(record)
                row={'condition':condition,'id':cid,'pilot':pilot,'judgement':judgement}
                rows.append(row);stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
                if wb:
                    try:wb.log({'judge/latency_seconds':judgement['latency_seconds'],'judge/valid_final':int(judgement['score'] is not None)})
                    except Exception:meta['wandb_status']='logging_error'
                return judgement['score'] is not None
            for cid in cfg['pilot_ids']:
                if ('main_mitigated',cid) in done:continue
                if not evaluate('main_mitigated',cid,pilot=True):
                    meta['stop_cause']='api_generation_or_format_failure';break
                if not pilot_summary(rows,[r['id'] for r in rows])['pilot_passed']:break
            pilot=pilot_summary(rows,cfg['pilot_ids'])
            (args.output/'pilot_summary.json').write_text(json.dumps(pilot,indent=2)+'\n',encoding='utf-8')
            meta['pilot_passed']=pilot['pilot_passed']
            if not pilot['pilot_passed']:
                meta['status']='stopped_api_or_format_failure' if meta.get('stop_cause') else 'completed_pilot_failed'
            else:
                for condition,cid in schedule():
                    if condition=='main_mitigated' and cid in cfg['pilot_ids']:continue
                    if not evaluate(condition,cid):
                        meta['stop_cause']='api_generation_or_format_failure';break
                summary=summarize(rows)
                name='partial_regression_summary.json' if meta.get('stop_cause') else 'regression_summary.json'
                (args.output/name).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
                meta.update(regression_gate_passed=summary['gate_passed'],
                    status='stopped_api_or_format_failure' if meta.get('stop_cause') else 'completed_regression_passed_confirmation_pending' if summary['gate_passed'] else 'completed_regression_failed')
    except Exception as exc:
        meta.update(status='failed',error_type=type(exc).__name__)
        if isinstance(exc,ApiFailure):meta.update(api_error_code=exc.code,http_status=exc.status)
        # No exception bodies/HTTP payloads/traceback locals that could expose credentials.
        print('Stopped safely:',meta['error_type'],meta.get('api_error_code',''),meta.get('http_status',''),flush=True)
    finally:
        meta['judgements_total']=len(rows)
        meta['judgements_executed']=len(rows)-meta.get('reused_valid_judgements',0)
        if generator:
            meta.update(generation_http_calls=generator.generation_calls,actual_model_version=generator.actual_version,technical_503_retries_used=generator.retry_count)
            if generator.last_error:meta['last_api_error']=generator.last_error
            try:
                meta['estimated_or_reserved_total_usd']=str(generator.ledger.used_or_reserved())
                ledger=generator.ledger.path.read_bytes()
                (args.output/'budget_ledger_snapshot.json').write_bytes(ledger)
                meta['budget_ledger_snapshot_sha256']=hashlib.sha256(ledger).hexdigest()
            except Exception:meta['budget_snapshot_error']=True
        if wb:
            try:
                wb.summary['execution_status']=meta['status'];wb.summary['judge_validated_for_final']=False;wb.finish()
                if meta['wandb_status']=='connected':meta['wandb_status']='finished_check_dashboard'
            except Exception:meta['wandb_status']='finish_error'
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(meta,ensure_ascii=False,indent=2))
    if meta['status']=='failed':sys.exit(1)


if __name__=='__main__':main()
