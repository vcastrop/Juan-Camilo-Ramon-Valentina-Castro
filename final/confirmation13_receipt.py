"""Offline evidence receipt; never signs a human review or dispatches an API call."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

from final.confirmation_final import summarize
from final.hydrogen_confirmation13 import verify_checkpoint, verify_approval
from final.judge_final import rubric_fingerprint
from final.paid_transition_preflight import read_archive
from final.prepare_eval_final import canonical_hash

SHA13 = 'e07af300b1395a2df624b47184168fd3fa4eb5d01e9e059eb21ab38da3b242f1'


def receive(root):
    root = Path(root)
    checkpoint = verify_checkpoint(root)
    approval = verify_approval(root)
    files = read_archive(root/'final/evidence/confirmation_13/original_results.zip', SHA13)
    meta = json.loads(files['metadata.json'])
    rows = [json.loads(s) for s in files['raw_judgements.jsonl'].decode().splitlines()]
    summary = summarize(rows)
    if not summary['gate_passed'] or summary != json.loads(files['confirmation_summary.json']):
        raise ValueError('Separate confirmation gate mismatch')
    if meta['approval_canonical_sha256'] != canonical_hash(approval) or meta['rubric_sha256'] != rubric_fingerprint():
        raise ValueError('Approval or rubric differs')
    if meta['generation_http_calls'] != 12 or meta['status'] != 'completed_confirmation_passed_semantic_audit_pending':
        raise ValueError('Unexpected confirmation run')
    for name, sha in meta['source_hashes'].items():
        if hashlib.sha256(subprocess.check_output(['git', 'show', meta['git_commit']+':'+name], cwd=root)).hexdigest() != sha:
            raise ValueError('Source hash mismatch')
    raw = files['budget_ledger_snapshot.json']
    if hashlib.sha256(raw).hexdigest() != meta['budget_ledger_snapshot_sha256']:
        raise ValueError('Budget hash mismatch')
    ledger = json.loads(raw)
    if ledger['limit_usd'] != '5.00' or len(ledger['requests']) != 57:
        raise ValueError('Unexpected cumulative ledger')
    for key, row in checkpoint['budget_snapshot']['requests'].items():
        if ledger['requests'].get(key) != row:
            raise ValueError('Prior reservation modified')
    responses = [json.loads(s) for s in files['api_requests.jsonl'].decode().splitlines()
                 if json.loads(s)['event'] == 'generation_response']
    new_ids = set(ledger['requests'])-set(checkpoint['budget_snapshot']['requests'])
    if len(responses) != 12 or len(new_ids) != 12 or {r['request_id'] for r in responses} != new_ids:
        raise ValueError('Response accounting mismatch')
    for response, row in zip(responses, rows):
        note = json.loads(response['raw_final'])
        if note['puntaje'] != row['judgement']['score'] or note['razon'] != row['judgement']['reason']:
            raise ValueError('Raw note differs')
    total = sum(Decimal(r['charged_or_reserved_usd']) for r in ledger['requests'].values())
    if total != Decimal('4.1974125'):
        raise ValueError('Cumulative total differs')
    margin = Decimal(5)-total
    reserve = Decimal('0.6144')
    # Descriptive planning only: product prompts may consume more than synthetic cases.
    mean_estimate = Decimal('0.49794')/Decimal(49)
    return {
        'status': 'confirmation_passed_human_semantic_closure_pending',
        'confirmation_summary': summary, 'original_metadata_changed': False,
        'judge_validated_for_final': False, 'human_review_signed_by_assistant': False,
        'network_requests_made_by_receipt': 0, 'authorized_total_usd': '5.00',
        'estimated_or_reserved_total_usd': str(total), 'margin_usd': str(margin),
        'per_dispatch_reservation_usd': str(reserve),
        'spendable_before_last_required_reservation_usd': str(margin-reserve),
        'actual_provider_invoice_usd': None,
        'planning_only': {
            'historical_new_paid_notes': 49, 'historical_conservative_estimate_usd': '0.49794',
            'historical_mean_estimate_per_note_usd': str(mean_estimate),
            'product_rows_to_score': 110,
            'illustrative_110_notes_cost_at_historical_mean_usd': str(mean_estimate*110),
            'warning': 'Not a forecast or spending authorization. Product evidence and thinking length differ. Do not select a favourable subset or lower the output cap silently.',
        },
    }


if __name__ == '__main__':
    print(json.dumps(receive(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2))
