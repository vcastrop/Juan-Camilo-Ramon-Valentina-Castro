"""Offline receipt for the billing transition. Never dispatches or changes a ledger."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import zipfile


FIRST_SHA = '67b8992833627382fcc20e5c9def59ebfffec6084c2a7fb813c26835d4ec3ac2'
BLOCKED_SHA = 'b704e1f819e4a2f9d6bcdbc6fefadbfad730942fa1de06679575ebbb02aa0c0b'


def read_archive(path, expected):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Evidence archive differs from received original')
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Corrupt evidence archive')
        return {n: archive.read(n) for n in archive.namelist() if not n.endswith('/')}


def transition_report(first, blocked, previous_ledger):
    meta = json.loads(first['metadata.json'])
    retry = json.loads(blocked['metadata.json'])
    ledger_raw = first['budget_ledger_snapshot.json']
    ledger = json.loads(ledger_raw)
    if hashlib.sha256(ledger_raw).hexdigest() != meta['budget_ledger_snapshot_sha256']:
        raise ValueError('Snapshot hash mismatch')
    if ledger['limit_usd'] != '5.00' or len(ledger['requests']) != 8:
        raise ValueError('Unexpected cumulative ledger')
    if len(previous_ledger['requests']) != 6:
        raise ValueError('Unexpected previous ledger')
    for key, row in previous_ledger['requests'].items():
        if ledger['requests'].get(key) != row:
            raise ValueError('Historical reservation changed')
    added = set(ledger['requests']) - set(previous_ledger['requests'])
    expected = {'status': 'reserved_before_dispatch',
                'charged_or_reserved_usd': '0.6144', 'worst_case_usd': '0.6144'}
    if len(added) != 2 or any(ledger['requests'][key] != expected for key in added):
        raise ValueError('Unexpected new reservations')
    total = sum((Decimal(row['charged_or_reserved_usd'])
                 for row in ledger['requests'].values()), Decimal(0))
    if total != Decimal('3.6994725') or meta['generation_http_calls'] != 2:
        raise ValueError('Unexpected first execution accounting')
    if retry.get('api_error_code') != 'same_drive_accounting_required_do_not_reset':
        raise ValueError('Unexpected second execution failure')
    if retry.get('judgements_executed') != 0 or 'api_requests.jsonl' in blocked:
        raise ValueError('Second execution needs separate dispatch audit')
    return {
        'status': 'awaiting_billing_evidence_and_versioned_paid_runner',
        'network_requests_made_by_this_check': 0,
        'paid_execution_allowed': False,
        'billing_enabled': 'user_reported_not_independently_verified',
        'free_attestation_in_second_run': 'inconsistent_with_user_report_do_not_reuse',
        'first_execution_generation_calls': 2,
        'second_execution_generation_calls': 0,
        'valid_judgements_reused': 1,
        'new_valid_judgements': 0,
        'judge_validated': False,
        'authorized_total_usd': '5.00',
        'estimated_or_reserved_usd': str(total),
        'local_unreserved_margin_usd': str(Decimal('5.00') - total),
        'margin_is_not_verified_provider_balance': True,
        'actual_provider_spend_usd': None,
        'ledger_snapshot_sha256': hashlib.sha256(ledger_raw).hexdigest(),
        'requirements_before_dispatch': [
            'Project billing state, dated usage and currency reviewed; reporting delay considered',
            'Current Drive ledger equals the latest eight-entry snapshot; no reset or release',
            'Existing started markers preserved; new versioned paid-mode marker required',
            'Current model pricing and per-request upper bound verified before dispatch',
            'Paid runner explicitly records billing mode, preserves valid scores and stops on failure',
            'Global USD 5 ceiling retained, including unknown reservations and other project usage',
        ],
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--blocked', type=Path, required=True)
    parser.add_argument('--previous', type=Path, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.previous) as archive:
        previous = json.loads(archive.read('budget_ledger_snapshot.json'))
    result = transition_report(read_archive(args.first, FIRST_SHA),
                               read_archive(args.blocked, BLOCKED_SHA), previous)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
