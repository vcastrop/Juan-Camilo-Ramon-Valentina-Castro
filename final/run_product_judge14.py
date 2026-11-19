"""Evaluate the complete saved comparison with the validated judge, no system generation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from final.api_budget7 import migrate, AUTHORIZATION
from final.gemini_judge_client import ApiFailure
from final.judge_final import FinalJudge, rubric_fingerprint
from final.product_judge14 import (
    checkpoint, register, product_plan, record_from_payload, ProductGenerator, POLICY,
)
from final.reasoning_calibration import request_seed


def summary(jobs):
    profiles = {}
    for profile in dict.fromkeys(j['profile'] for j in jobs):
        selected = [j for j in jobs if j['profile'] == profile]
        scores = [j['judgement']['score'] for j in selected
                  if j.get('judgement') and j['judgement']['score'] is not None]
        complete = len(selected) == 22 and len(scores) == 22
        profiles[profile] = {'expected_cases': 22, 'valid_judgements': len(scores),
                             'complete': complete, 'judge_mean_1_5': sum(scores)/22 if complete else None,
                             'domain_compliance_rate': None}
    return {'expected_cases': 110, 'complete': len(jobs) == 110 and all(p['complete'] for p in profiles.values()),
            'profiles': profiles, 'domain_status': 'pending_semantic_join_and_judge_reason_audit',
            'warning': 'Scores are unadjusted judge outputs, not accuracy or a completed domain scorecard. Incomplete profiles have no published mean.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-dir', type=Path, required=True)
    parser.add_argument('--confirm-paid-project', action='store_true')
    parser.add_argument('--confirm-exclusive-budget-use', action='store_true')
    parser.add_argument('--confirm-total-usd7', action='store_true')
    parser.add_argument('--require-wandb', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Do not overwrite or repeat product evaluation; preserve all evidence')
    args.output.mkdir(parents=True)
    jobs, generator, wb = [], None, None
    meta = {'status': 'started', 'purpose': 'saved_product_responses_judge14',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'policy': POLICY,
            'authorization': AUTHORIZATION, 'actual_invoice_verified': False,
            'free_project_attested': False, 'outputs_regenerated': False,
            'calibration_regenerated': False, 'gold_in_judge_payload': False,
            'score_adjusted': False, 'wandb_status': 'disabled', 'historical_generation_http_calls': 57,
            'generation_http_calls': 0, 'paid_dispatch_authorized': False,
            'expected_product_cases': 110, 'rubric_sha256': rubric_fingerprint()}

    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    save()
    try:
        if not (args.confirm_paid_project and args.confirm_exclusive_budget_use and args.confirm_total_usd7):
            raise ApiFailure('paid_exclusive_use_and_usd7_total_confirmation_required')
        if datetime.now(timezone.utc).date().isoformat() > POLICY['price_recheck_after_utc']:
            raise ApiFailure('price_recheck_required')
        if not os.environ.get('GEMINI_API_KEY'):
            raise ApiFailure('missing_api_key')
        saved = checkpoint(ROOT)
        cfg = json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'))
        plan = product_plan(ROOT)
        jobs = plan['jobs']
        (args.output/'original_execution_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        meta.update(judge_approved_for_this_configuration=True,
                    human_closure_sha256=plan['judge_human_closure_sha256'],
                    source_comparison_sha256=plan['source_comparison_sha256'],
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
        names = ['final/run_product_judge14.py', 'final/product_judge14.py', 'final/api_budget7.py',
                 'final/prepare_product_judge_plan.py', 'final/human_closure_receipt.py',
                 'final/confirmation13_receipt.py', 'final/judge_final.py', 'final/hydrogen_paid12.py',
                 'final/hydrogen_judge_client.py', 'final/hydrogen_recovery11.py',
                 'final/reasoning_calibration.py', 'm3/judge.py']
        meta['source_hashes'] = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
        if os.environ.get('WANDB_API_KEY'):
            import wandb
            wb = wandb.init(entity='jcramonp-eanit', project='contractrisk-final', job_type='saved-product-judge',
                config={'policy': POLICY, 'commit': meta['git_commit']}, settings=wandb.Settings(
                    disable_git=True, disable_code=True, disable_job_creation=True, x_disable_stats=True, init_timeout=30))
            meta.update(wandb_status='connected', wandb_url=wb.url, wandb_run_id=wb.id)
        if args.require_wandb and wb is None:
            raise ApiFailure('wandb_unavailable_before_api_dispatch')
        register(args.budget_dir, cfg, saved)
        meta['budget_migration'] = migrate(args.budget_dir, saved['budget_snapshot'], confirmed_total_usd7=True)
        generator = ProductGenerator(os.environ['GEMINI_API_KEY'], cfg,
            args.budget_dir/'api_budget_ledger.json', args.output/'api_requests.jsonl', checkpoint=saved,
            confirmed_paid_project=True, confirmed_total_usd7=True, exclusive_project_use=True)
        meta['model_preflight'] = generator.preflight()
        meta['paid_dispatch_authorized'] = True
        save()
        with (args.output/'raw_judgements.jsonl').open('x', encoding='utf-8') as stream:
            for index, job in enumerate(jobs, 1):
                print('Product judge:', index, '/110', job['profile'], job['id'], flush=True)
                generator.set_request_seed(request_seed(job['id'], cfg['seed']))
                judgement = FinalJudge(generator).evaluate(record_from_payload(job['judge_payload']))
                job.update(judgement=judgement, dispatch_status='valid' if judgement['score'] is not None else 'failed')
                row = {k: job[k] for k in ['profile', 'id', 'source_record_sha256', 'payload_sha256', 'judgement']}
                stream.write(json.dumps(row, ensure_ascii=False)+'\n')
                stream.flush()
                if wb:
                    try:
                        wb.log({'judge/valid': int(judgement['score'] is not None),
                                'judge/latency_seconds': judgement['latency_seconds'], 'judge/completed_case_index': index})
                    except Exception:
                        meta['wandb_status'] = 'logging_error'
                if judgement['score'] is None:
                    meta['stop_cause'] = 'api_format_or_budget_failure_no_automatic_retry'
                    break
        result = summary(jobs)
        meta['status'] = 'completed_110_judgements_audit_pending' if result['complete'] else 'stopped_partial_evaluation'
    except Exception as exc:
        meta.update(status='failed', error_type=type(exc).__name__)
        if isinstance(exc, ApiFailure):
            meta.update(api_error_code=exc.code, http_status=exc.status)
        print('Stopped safely:', meta['error_type'], meta.get('api_error_code', ''), flush=True)
    finally:
        meta['judgements_attempted'] = sum(j.get('judgement') is not None for j in jobs)
        meta['valid_product_judgements'] = sum(j.get('judgement') is not None and j['judgement']['score'] is not None for j in jobs)
        if jobs:
            (args.output/'execution_manifest.json').write_text(json.dumps(jobs, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            (args.output/'judge_summary.json').write_text(json.dumps(summary(jobs), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if generator:
            meta.update(generation_http_calls=generator.generation_calls, technical_retries=0,
                        last_api_error=generator.last_error, actual_model_version=generator.actual_version,
                        model_version_inherited_from_checkpoint=generator.observed_response_count == 0)
            try:
                meta['estimated_or_reserved_total_usd'] = str(generator.ledger.used_or_reserved())
            except Exception:
                meta['budget_snapshot_error'] = True
        # Also preserve accounting if migration succeeded but client construction failed.
        try:
            raw = (args.budget_dir/'api_budget_ledger.json').read_bytes()
            (args.output/'budget_ledger_snapshot.json').write_bytes(raw)
            meta['budget_ledger_snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
            for name in ['api_budget_authorization_usd7.json', 'api_budget_ledger_before_usd7.json']:
                path = args.budget_dir/name
                if path.exists(): (args.output/name).write_bytes(path.read_bytes())
        except Exception:
            meta['budget_snapshot_error'] = True
        if wb:
            try:
                wb.summary['execution_status'] = meta['status']
                wb.summary['product_judgements_complete'] = meta['valid_product_judgements'] == 110
                wb.finish()
                meta['wandb_status'] = 'finished_check_dashboard'
            except Exception:
                meta['wandb_status'] = 'finish_error'
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if meta['status'] == 'failed': sys.exit(1)


if __name__ == '__main__':
    main()
