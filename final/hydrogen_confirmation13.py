"""Frozen separate confirmation after paid calibration; no final product scores."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

from final.calibration_final import summarize as calibration_summary
from final.confirmation_final import cases, RULES
from final.gemini_judge_client import ApiFailure
from final.hydrogen_paid12 import PaidGenerator, verify_checkpoint as verify11, POLICY as POLICY12
from final.judge_final import rubric_fingerprint
from final.paid_transition_preflight import read_archive
from final.prepare_eval_final import canonical_hash

SHA12 = 'b69d2741286ae85c2400d9412599337f6ab66dbdb516fbd1b5b3186f9b73ec45'
POLICY = {**POLICY12, 'version': 'hydrogen-confirmation-13', 'cases': 12,
          'calibration_scores_regenerated': False, 'final_gold_loaded': False,
          'confirmation_rules_changed': False, 'stop_on_first_invalid_or_bad_accepted': True}


def verify_approval(root):
    root = Path(root)
    pack = root/'final/eval/confirmation_v1'
    approval = json.loads((pack/'human_approval.json').read_text(encoding='utf-8'))
    checks = {
        'status': 'approved', 'anchors_canonical_sha256': canonical_hash(cases()),
        'rules_canonical_sha256': canonical_hash(RULES), 'rubric_sha256': rubric_fingerprint(),
    }
    if any(approval.get(k) != v for k, v in checks.items()):
        raise ValueError('Separate confirmation approval missing or changed')
    ids = approval.get('approved_ids', [])
    if len(ids) != 12 or set(ids) != {c['id'] for c in cases()}:
        raise ValueError('All twelve cases must be approved before execution')
    if json.loads((pack/'anchors.json').read_text(encoding='utf-8')) != cases():
        raise ValueError('Confirmation pack differs from frozen cases')
    if json.loads((pack/'rules.json').read_text(encoding='utf-8')) != RULES:
        raise ValueError('Confirmation rules changed')
    original = (root/'final/evidence/confirmation_review_01/original_review.md').read_bytes()
    if hashlib.sha256(original).hexdigest() != approval['original_review_sha256']:
        raise ValueError('Original human review changed')
    return approval


def verify_checkpoint(root):
    root = Path(root)
    previous = verify11(root)
    files = read_archive(root/'final/evidence/paid_12/original_results.zip', SHA12)
    meta = json.loads(files['metadata.json'])
    rows = [json.loads(s) for s in files['raw_judgements.jsonl'].decode().splitlines()]
    summary = calibration_summary(rows)
    if not summary['gate_passed'] or summary != json.loads(files['regression_summary.json']):
        raise ValueError('Calibration did not pass unchanged gates')
    if meta['status'] != 'completed_regression_passed_confirmation_pending' or meta['generation_http_calls'] != 37:
        raise ValueError('Unexpected calibration execution')
    if meta['rubric_sha256'] != rubric_fingerprint() or meta['actual_model_version'] != 'gemini-4-hydrogen':
        raise ValueError('Model or rubric changed')
    for name, expected in meta['source_hashes'].items():
        data = subprocess.check_output(['git', 'show', meta['git_commit']+':'+name], cwd=root)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Historical source hash mismatch')
    raw = files['budget_ledger_snapshot.json']
    if hashlib.sha256(raw).hexdigest() != meta['budget_ledger_snapshot_sha256']:
        raise ValueError('Budget snapshot changed')
    ledger = json.loads(raw)
    if len(ledger['requests']) != 45 or ledger['limit_usd'] != '5.00':
        raise ValueError('Unexpected cumulative ledger')
    if sum(Decimal(r['charged_or_reserved_usd']) for r in ledger['requests'].values()) != Decimal('4.0800825'):
        raise ValueError('Unexpected cumulative amount')
    for key, row in previous['budget_snapshot']['requests'].items():
        if ledger['requests'].get(key) != row:
            raise ValueError('Older reservation altered')
    responses = [json.loads(s) for s in files['api_requests.jsonl'].decode().splitlines()
                 if json.loads(s)['event'] == 'generation_response']
    new_ids = set(ledger['requests']) - set(previous['budget_snapshot']['requests'])
    if len(responses) != 37 or {r['request_id'] for r in responses} != new_ids:
        raise ValueError('Response ledger mismatch')
    for response, row in zip(responses, rows[1:]):
        note = json.loads(response['raw_final'])
        if note['puntaje'] != row['judgement']['score'] or note['razon'] != row['judgement']['reason']:
            raise ValueError('Public raw note changed')
    if rows[0]['judgement'] != previous['saved_rows'][0]['judgement']:
        raise ValueError('Historical valid note changed')
    previous['metadata'] = meta
    previous['budget_snapshot'] = ledger
    previous['base_drive']['budget_snapshot'] = ledger
    previous['financial_checkpoint_archive_sha256'] = SHA12
    return previous


def check_drive(folder, cfg, checkpoint):
    from final.hydrogen_paid12 import check_drive as check12
    check12(folder, cfg, checkpoint)
    path = Path(folder)/'hydrogen_paid_12.started.json'
    if not path.is_file():
        raise ApiFailure('paid12_marker_required')
    marker = json.loads(path.read_text(encoding='utf-8'))
    if (marker.get('policy') != POLICY12 or marker.get('generation_config_sha256') != canonical_hash(cfg)
            or marker.get('financial_checkpoint_archive_sha256') != '67b8992833627382fcc20e5c9def59ebfffec6084c2a7fb813c26835d4ec3ac2'):
        raise ApiFailure('paid12_marker_changed')


def register_confirmation(folder, cfg, checkpoint):
    from datetime import datetime, timezone
    check_drive(folder, cfg, checkpoint)
    with (Path(folder)/'hydrogen_confirmation_13.started.json').open('x', encoding='utf-8') as stream:
        json.dump({'started_utc': datetime.now(timezone.utc).isoformat(), 'policy': POLICY,
                   'generation_config_sha256': canonical_hash(cfg), 'calibration_archive_sha256': SHA12}, stream, indent=2)


class ConfirmationGenerator(PaidGenerator):
    def __init__(self, key, cfg, ledger_path, audit_path, *, checkpoint, **kwargs):
        check_drive(Path(ledger_path).parent, cfg, checkpoint)
        super().__init__(key, cfg, ledger_path, audit_path, checkpoint=checkpoint, **kwargs)

    def journal(self, entry):
        super().journal({**entry, 'protocol': POLICY['version']})
