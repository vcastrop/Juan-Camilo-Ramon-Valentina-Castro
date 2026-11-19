import copy
import json
from pathlib import Path
import unittest
import zipfile

from final.paid_transition_preflight import (
    FIRST_SHA, BLOCKED_SHA, read_archive, transition_report,
)

ROOT = Path(__file__).resolve().parents[2]


class PaidTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = read_archive(ROOT/'final/evidence/hydrogen_11/original_results.zip', FIRST_SHA)
        cls.blocked = read_archive(ROOT/'final/evidence/hydrogen_11_billing_rerun/original_results.zip', BLOCKED_SHA)
        with zipfile.ZipFile(ROOT/'final/evidence/hydrogen_10/original_results.zip') as archive:
            cls.previous = json.loads(archive.read('budget_ledger_snapshot.json'))

    def test_real_transition_stays_offline_and_blocked(self):
        result = transition_report(self.first, self.blocked, self.previous)
        self.assertFalse(result['paid_execution_allowed'])
        self.assertIsNone(result['actual_provider_spend_usd'])
        self.assertEqual(result['local_unreserved_margin_usd'], '1.3005275')
        self.assertEqual(result['second_execution_generation_calls'], 0)
        self.assertEqual(result['new_valid_judgements'], 0)

    def test_archive_change_rejected(self):
        with self.assertRaises(ValueError):
            read_archive(ROOT/'final/evidence/hydrogen_11/original_results.zip', '0'*64)

    def test_historical_reservation_change_rejected(self):
        previous = copy.deepcopy(self.previous)
        next(iter(previous['requests'].values()))['charged_or_reserved_usd'] = '0'
        with self.assertRaisesRegex(ValueError, 'Historical reservation'):
            transition_report(self.first, self.blocked, previous)

    def test_dispatch_evidence_not_silently_ignored(self):
        changed = dict(self.blocked, **{'api_requests.jsonl': b'{}\n'})
        with self.assertRaisesRegex(ValueError, 'separate dispatch audit'):
            transition_report(self.first, changed, self.previous)

    def test_changed_failure_not_called_pre_dispatch_block(self):
        changed = dict(self.blocked)
        meta = json.loads(changed['metadata.json'])
        meta['api_error_code'] = 'api_http_error'
        changed['metadata.json'] = json.dumps(meta).encode()
        with self.assertRaisesRegex(ValueError, 'Unexpected second'):
            transition_report(self.first, changed, self.previous)

    def test_snapshot_tampering_rejected(self):
        changed = dict(self.first)
        changed['budget_ledger_snapshot.json'] += b' '
        with self.assertRaisesRegex(ValueError, 'Snapshot hash'):
            transition_report(changed, self.blocked, self.previous)
