"""Continue synthetic calibration in explicitly confirmed paid mode; never final gold."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from final.calibration_final import cases, schedule, summarize, verbose
from final.gemini_judge_client import ApiFailure
from final.hydrogen_paid12 import PaidGenerator, verify_checkpoint, register_paid, POLICY
from final.judge_final import FinalJudge, rubric_fingerprint
from final.reasoning_calibration import request_seed
from final.run_hydrogen_recovery11 import pilot_summary
from final.run_judge_calibration import verify_review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-dir', type=Path, required=True)
    parser.add_argument('--confirm-paid-project', action='store_true')
    parser.add_argument('--confirm-exclusive-budget-use', action='store_true')
    parser.add_argument('--require-wandb', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new result directory; do not overwrite evidence')
    args.output.mkdir(parents=True)
    meta = {'status': 'started', 'purpose': 'synthetic_paid_calibration_continuation_12',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'policy': POLICY,
            'billing_mode': POLICY['billing_mode'], 'free_project_attested': False,
            'billing_evidence': 'user_screenshots_paid_tier1_prepay_autoreload_off_cost_delayed',
            'actual_invoice_verified': False, 'judge_validated_for_final': False,
            'final_gold_loaded': False, 'confirmation_executed': False,
            'score_adjusted': False, 'wandb_status': 'disabled'}
    rows = []
    generator = None
    wb = None

    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    save()
    try:
        if not args.confirm_paid_project or not args.confirm_exclusive_budget_use:
            raise ApiFailure('paid_project_and_exclusive_budget_confirmation_required')
        verify_review(ROOT/'final/eval/calibration_review_v1')
        cfg = json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'))
        checkpoint = verify_checkpoint(ROOT)
        rows = copy.deepcopy(checkpoint['saved_rows'])
        meta.update(historical_generation_http_calls=8, reused_valid_judgements=1,
                    financial_checkpoint_archive_sha256=checkpoint['financial_checkpoint_archive_sha256'],
                    rubric_sha256=rubric_fingerprint(),
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
        source_names = ['final/hydrogen_paid12.py', 'final/run_hydrogen_paid12.py',
                        'final/paid_transition_preflight.py', 'final/hydrogen_judge_client.py',
                        'final/hydrogen_recovery11.py', 'final/hydrogen_resume.py',
                        'final/api_budget.py', 'final/judge_final.py', 'final/calibration_final.py',
                        'final/reasoning_calibration.py', 'm3/judge.py']
        meta['source_hashes'] = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in source_names}
        generator = PaidGenerator(os.environ.get('GEMINI_API_KEY'), cfg,
                                  args.budget_dir/'api_budget_ledger.json', args.output/'api_requests.jsonl',
                                  checkpoint=checkpoint, confirmed_paid_project=True, exclusive_project_use=True)
        if os.environ.get('WANDB_API_KEY'):
            import wandb
            wb = wandb.init(entity='jcramonp-eanit', project='contractrisk-final', job_type='synthetic-paid-judge',
                            config={'policy': POLICY, 'commit': meta['git_commit']},
                            settings=wandb.Settings(disable_git=True, disable_code=True, disable_job_creation=True,
                                                   x_disable_stats=True, init_timeout=30))
            meta.update(wandb_status='connected', wandb_url=wb.url, wandb_run_id=wb.id)
        if args.require_wandb and wb is None:
            raise ApiFailure('wandb_unavailable_before_api_dispatch')
        register_paid(args.budget_dir, cfg, checkpoint)
        meta['model_preflight'] = generator.preflight()
        save()
        anchors = {c['id']: c['record'] for c in cases()}
        with (args.output/'raw_judgements.jsonl').open('x', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False)+'\n')
            stream.flush()

            def evaluate(condition, cid):
                print('API judge:', condition, cid, flush=True)
                record = verbose(anchors[cid]) if condition.endswith('verbose') else anchors[cid]
                generator.set_request_seed(request_seed(cid, cfg['seed']))
                judgement = FinalJudge(generator, mitigate_verbosity=not condition.startswith('before_')).evaluate(record)
                rows.append({'condition': condition, 'id': cid, 'judgement': judgement})
                stream.write(json.dumps(rows[-1], ensure_ascii=False)+'\n')
                stream.flush()
                return judgement['score'] is not None

            for cid in cfg['pilot_ids']:
                if cid == rows[0]['id']:
                    continue
                if not evaluate('main_mitigated', cid):
                    meta['stop_cause'] = 'api_or_format_failure'
                    break
                if not pilot_summary(rows, [r['id'] for r in rows])['pilot_passed']:
                    break
            pilot = pilot_summary(rows, cfg['pilot_ids'])
            (args.output/'pilot_summary.json').write_text(json.dumps(pilot, indent=2), encoding='utf-8')
            meta['pilot_passed'] = pilot['pilot_passed']
            if pilot['pilot_passed']:
                for condition, cid in schedule():
                    if condition == 'main_mitigated' and cid in cfg['pilot_ids']:
                        continue
                    if not evaluate(condition, cid):
                        meta['stop_cause'] = 'api_or_format_failure'
                        break
                summary = summarize(rows)
                (args.output/'regression_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
                meta['regression_gate_passed'] = summary['gate_passed']
                meta['status'] = ('stopped_api_or_format_failure' if meta.get('stop_cause') else
                                  'completed_regression_passed_confirmation_pending' if summary['gate_passed'] else
                                  'completed_regression_failed')
            else:
                meta['status'] = 'stopped_api_or_format_failure' if meta.get('stop_cause') else 'completed_pilot_failed'
    except Exception as exc:
        meta.update(status='failed', error_type=type(exc).__name__)
        if isinstance(exc, ApiFailure):
            meta.update(api_error_code=exc.code, http_status=exc.status)
        print('Stopped safely:', meta['error_type'], meta.get('api_error_code', ''), flush=True)
    finally:
        meta.update(judgements_total=len(rows), judgements_executed=max(0, len(rows)-1))
        if generator:
            meta.update(generation_http_calls=generator.generation_calls, last_api_error=generator.last_error,
                        actual_model_version=generator.actual_version, technical_retries=0,
                        model_version_inherited_from_checkpoint=generator.generation_calls == 0)
            try:
                meta['estimated_or_reserved_total_usd'] = str(generator.ledger.used_or_reserved())
                raw = generator.ledger.path.read_bytes()
                (args.output/'budget_ledger_snapshot.json').write_bytes(raw)
                meta['budget_ledger_snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
            except Exception:
                meta['budget_snapshot_error'] = True
        if wb:
            try:
                wb.summary['execution_status'] = meta['status']
                wb.summary['judge_validated_for_final'] = False
                wb.finish()
                meta['wandb_status'] = 'finished_check_dashboard'
            except Exception:
                meta['wandb_status'] = 'finish_error'
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if meta['status'] == 'failed':
        sys.exit(1)


if __name__ == '__main__':
    main()
