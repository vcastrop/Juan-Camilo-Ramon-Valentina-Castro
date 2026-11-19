"""Run only the twelve previously approved separate confirmation cases."""
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
from final.confirmation_final import cases, summarize
from final.gemini_judge_client import ApiFailure
from final.hydrogen_confirmation13 import (
    ConfirmationGenerator, verify_checkpoint, verify_approval, register_confirmation, POLICY, SHA12,
)
from final.judge_final import FinalJudge, rubric_fingerprint
from final.prepare_eval_final import canonical_hash
from final.reasoning_calibration import request_seed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-dir', type=Path, required=True)
    parser.add_argument('--confirm-paid-project', action='store_true')
    parser.add_argument('--confirm-exclusive-budget-use', action='store_true')
    parser.add_argument('--require-wandb', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Do not overwrite or repeat confirmation')
    args.output.mkdir(parents=True)
    rows, generator, wb = [], None, None
    meta = {'status': 'started', 'purpose': 'separate_synthetic_confirmation_13',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'policy': POLICY,
            'billing_mode': POLICY['billing_mode'], 'free_project_attested': False,
            'judge_validated_for_final': False, 'actual_invoice_verified': False,
            'final_gold_loaded': False, 'score_adjusted': False, 'wandb_status': 'disabled',
            'calibration_archive_sha256': SHA12, 'calibration_scores_regenerated': False,
            'historical_generation_http_calls': 45, 'rubric_sha256': rubric_fingerprint()}

    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    save()
    try:
        if not args.confirm_paid_project or not args.confirm_exclusive_budget_use:
            raise ApiFailure('paid_project_and_exclusive_budget_confirmation_required')
        approval = verify_approval(ROOT)
        checkpoint = verify_checkpoint(ROOT)
        cfg = json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'))
        meta.update(approval_canonical_sha256=canonical_hash(approval),
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
        names = ['final/hydrogen_confirmation13.py', 'final/run_hydrogen_confirmation13.py',
                 'final/confirmation_final.py', 'final/hydrogen_paid12.py', 'final/hydrogen_judge_client.py',
                 'final/api_budget.py', 'final/judge_final.py', 'final/reasoning_calibration.py', 'm3/judge.py']
        meta['source_hashes'] = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
        generator = ConfirmationGenerator(os.environ.get('GEMINI_API_KEY'), cfg,
            args.budget_dir/'api_budget_ledger.json', args.output/'api_requests.jsonl', checkpoint=checkpoint,
            confirmed_paid_project=True, exclusive_project_use=True)
        if os.environ.get('WANDB_API_KEY'):
            import wandb
            wb = wandb.init(entity='jcramonp-eanit', project='contractrisk-final', job_type='separate-judge-confirmation',
                config={'policy': POLICY, 'commit': meta['git_commit']}, settings=wandb.Settings(
                    disable_git=True, disable_code=True, disable_job_creation=True, x_disable_stats=True, init_timeout=30))
            meta.update(wandb_status='connected', wandb_url=wb.url, wandb_run_id=wb.id)
        if args.require_wandb and wb is None:
            raise ApiFailure('wandb_unavailable_before_api_dispatch')
        register_confirmation(args.budget_dir, cfg, checkpoint)
        meta['model_preflight'] = generator.preflight()
        save()
        with (args.output/'raw_judgements.jsonl').open('x', encoding='utf-8') as stream:
            for case in cases():
                print('Confirmation:', case['id'], flush=True)
                generator.set_request_seed(request_seed(case['id'], cfg['seed']))
                # Expected ranges and good/bad flags are never sent to the judge.
                judgement = FinalJudge(generator).evaluate(case['record'])
                rows.append({'id': case['id'], 'judgement': judgement})
                stream.write(json.dumps(rows[-1], ensure_ascii=False)+'\n')
                stream.flush()
                score = judgement['score']
                if score is None:
                    meta['stop_cause'] = 'api_format_or_budget_failure'
                    break
                if case['group'] == 'bad' and score >= 4:
                    meta['stop_cause'] = 'bad_answer_accepted_no_resampling'
                    break
        summary = summarize(rows)
        (args.output/'confirmation_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        meta.update(confirmation_gate_passed=summary['gate_passed'],
                    status='completed_confirmation_passed_semantic_audit_pending' if summary['gate_passed'] else 'confirmation_failed_or_incomplete')
    except Exception as exc:
        meta.update(status='failed', error_type=type(exc).__name__)
        if isinstance(exc, ApiFailure):
            meta.update(api_error_code=exc.code, http_status=exc.status)
        print('Stopped safely:', meta['error_type'], meta.get('api_error_code', ''), flush=True)
    finally:
        meta['judgements_executed'] = len(rows)
        if generator:
            meta.update(generation_http_calls=generator.generation_calls, last_api_error=generator.last_error,
                        technical_retries=0, actual_model_version=generator.actual_version,
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
