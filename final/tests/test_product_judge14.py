import copy
import contextlib
from datetime import datetime, timezone
from decimal import Decimal
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from final.api_budget7 import migrate, BudgetLedger7, BACKUP, AUTH_FILE
from final.api_budget import BudgetLedger
from final.gemini_judge_client import ApiFailure
from final.hydrogen_confirmation13 import POLICY as POLICY13
from final.prepare_eval_final import canonical_hash
from final.product_judge14 import checkpoint, check_drive, register, product_plan, record_from_payload, ProductGenerator
from final.tests import test_confirmation13 as fixtures
from final.tests.test_hydrogen_judge import config, Transport

ROOT = Path(__file__).resolve().parents[2]


class Product14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = checkpoint(ROOT)
        cls.plan = product_plan(ROOT)

    def drive(self, folder):
        # Fixture helper expects .checkpoint; no real Drive or API calls in tests.
        self.checkpoint = self.saved
        fixtures.Confirmation13Tests.drive(self, folder)
        (Path(folder)/'hydrogen_confirmation_13.started.json').write_text(json.dumps({
            'policy': POLICY13, 'generation_config_sha256': canonical_hash(config()),
            'calibration_archive_sha256': 'b69d2741286ae85c2400d9412599337f6ab66dbdb516fbd1b5b3186f9b73ec45'}), encoding='utf-8')

    def setup7(self, folder):
        self.drive(folder)
        register(folder, config(), self.saved)
        return migrate(folder, self.saved['budget_snapshot'], confirmed_total_usd7=True)

    def client(self, folder, error=None, **kwargs):
        fake = Transport(score=2, error=error)
        def send(method, path, body):
            return self.saved['metadata']['model_preflight'] if method == 'GET' else fake(method, path, body)
        params = dict(confirmed_paid_project=True, confirmed_total_usd7=True, exclusive_project_use=True,
                      transport=send, now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc),
                      clock=lambda: 0, sleeper=lambda _: None)
        params.update(kwargs)
        return ProductGenerator('FAKE', config(), Path(folder)/'api_budget_ledger.json', Path(folder)/'calls.jsonl',
                                checkpoint=self.saved, **params)

    def test_migration_preserves_all_57_entries_and_old_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            path = Path(temp)/'api_budget_ledger.json'
            before = path.read_bytes()
            markers = {p.name: p.read_bytes() for p in Path(temp).glob('*.started.json')}
            migrate(temp, self.saved['budget_snapshot'], confirmed_total_usd7=True)
            after = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(after['limit_usd'], '7.00')
            self.assertEqual(after['requests'], self.saved['budget_snapshot']['requests'])
            self.assertEqual((Path(temp)/BACKUP).read_bytes(), before)
            for name, raw in markers.items(): self.assertEqual((Path(temp)/name).read_bytes(), raw)
            with self.assertRaises(ValueError): migrate(temp, self.saved['budget_snapshot'], confirmed_total_usd7=True)

    def test_no_implicit_initialization_or_unconfirmed_migration(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            with self.assertRaises(ValueError): migrate(temp, self.saved['budget_snapshot'])
            with self.assertRaises(ValueError): BudgetLedger7(Path(temp)/'api_budget_ledger.json').used_or_reserved()
            (Path(temp)/'api_budget_ledger.json').unlink()
            with self.assertRaises(FileNotFoundError): BudgetLedger7(Path(temp)/'api_budget_ledger.json').used_or_reserved()

    def test_historical_entries_cannot_be_released(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            path = Path(temp)/'api_budget_ledger.json'
            data = json.loads(path.read_text())
            next(iter(data['requests'].values()))['charged_or_reserved_usd'] = '0'
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): BudgetLedger7(path).reserve('0.6144')

    def test_existing_lock_is_not_removed_or_bypassed(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            path = Path(temp)/'api_budget_ledger.json'
            lock = path.with_suffix('.json.lock')
            lock.write_bytes(b'Existing owner')
            before = path.read_bytes()
            with self.assertRaises(FileExistsError): migrate(temp, self.saved['budget_snapshot'], confirmed_total_usd7=True)
            self.assertEqual(lock.read_bytes(), b'Existing owner')
            self.assertEqual(path.read_bytes(), before)

    def test_backup_or_authorization_tampering_blocks_dispatch(self):
        for name in [BACKUP, AUTH_FILE]:
            with tempfile.TemporaryDirectory() as temp:
                self.setup7(temp)
                (Path(temp)/name).write_text('{}', encoding='utf-8')
                with self.assertRaises((ValueError, KeyError)): self.client(temp)

    def test_total7_not_7_additional_and_legacy_client_refuses_it(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            ledger = BudgetLedger7(Path(temp)/'api_budget_ledger.json')
            ledger.reserve('2.80')
            with self.assertRaises(RuntimeError): ledger.reserve('0.01')
            with self.assertRaises(ValueError): BudgetLedger(ledger.path).used_or_reserved()
            self.assertEqual(ledger.used_or_reserved(), Decimal('6.9974125'))

    def test_budget_above_reservation_blocks_subsequent_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            ledger = BudgetLedger7(Path(temp)/'api_budget_ledger.json')
            key = ledger.reserve('0.10')
            with self.assertRaises(RuntimeError): ledger.settle(key, '0.11')
            with self.assertRaises(RuntimeError): ledger.reserve('0.01')

    def test_503_has_one_dispatch_and_keeps_unknown_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            client = self.client(temp, ApiFailure('api_http_error', 503))
            client.preflight()
            with self.assertRaises(ApiFailure): client.generate('s', 'u')
            self.assertEqual(client.generation_calls, 1)
            self.assertEqual(client.ledger.used_or_reserved(), Decimal('4.8118125'))

    def test_configuration_and_payload_unchanged_and_complete_plan(self):
        from final.hydrogen_judge_client import HydrogenRESTGenerator
        from m3.judge import evidence_payload
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            client = self.client(temp)
            # Request construction does not depend on the authorized budget fields.
            body = client.request_body('s', 'u')
            self.assertEqual(body['generationConfig']['maxOutputTokens'], 65536)
            self.assertEqual(body['generationConfig']['thinkingConfig']['thinkingLevel'], 'HIGH')
            self.assertEqual(self.plan['current_authorized_total_usd'], '7.00')
            self.assertEqual(len(self.plan['jobs']), 110)
            for job in self.plan['jobs']:
                self.assertEqual(evidence_payload(record_from_payload(job['judge_payload'])), job['judge_payload'])

    def test_runtime_confirmation_and_price_expiry_required(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup7(temp)
            with self.assertRaises(ApiFailure): self.client(temp, confirmed_total_usd7=False)
            with self.assertRaises(ApiFailure): self.client(temp, now_utc=datetime(2026, 11, 21, tzinfo=timezone.utc))

    def test_full110_runner_keeps_low_scores_and_no_domain_invention(self):
        self.run_scenario(None, 110)

    def test_runner_stops_on_first_transport_failure_and_blocks_rerun(self):
        self.run_scenario(ApiFailure('api_http_error', 503), 1)

    def run_scenario(self, error, expected_calls):
        from final import run_product_judge14 as runner
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'drive'
            folder.mkdir()
            self.drive(folder)
            clients = []
            def factory(key, cfg, ledger_path, audit_path, **kwargs):
                fake = Transport(score=2, error=error)
                def send(method, path, body):
                    return self.saved['metadata']['model_preflight'] if method == 'GET' else fake(method, path, body)
                client = ProductGenerator(key, cfg, ledger_path, audit_path, **kwargs, transport=send,
                    now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc), clock=lambda: 0, sleeper=lambda _: None)
                clients.append(client)
                return client
            class FixedTime:
                @staticmethod
                def now(tz): return datetime(2026, 11, 19, tzinfo=timezone.utc)
            def run(output):
                argv = ['judge14', '--output', str(output), '--budget-dir', str(folder),
                        '--confirm-paid-project', '--confirm-exclusive-budget-use', '--confirm-total-usd7']
                with patch.object(sys, 'argv', argv), patch.dict('os.environ', {'GEMINI_API_KEY': 'FAKE', 'WANDB_API_KEY': ''}), \
                     patch.object(runner, 'ProductGenerator', side_effect=factory), patch.object(runner, 'datetime', FixedTime), \
                     contextlib.redirect_stdout(io.StringIO()):
                    runner.main()
            output = Path(temp)/'results'
            run(output)
            meta = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            result = json.loads((output/'judge_summary.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['generation_http_calls'], expected_calls)
            self.assertEqual(result['complete'], error is None)
            self.assertEqual(len(json.loads((output/'execution_manifest.json').read_text(encoding='utf-8'))), 110)
            for p in result['profiles'].values():
                self.assertIsNone(p['domain_compliance_rate'])
                self.assertEqual(p['judge_mean_1_5'], 2 if error is None else None)
            self.assertLess(Decimal(meta['estimated_or_reserved_total_usd']), Decimal(7))
            with self.assertRaises(SystemExit): run(Path(temp)/'repeat')
            self.assertEqual(sum(c.generation_calls for c in clients), expected_calls)
