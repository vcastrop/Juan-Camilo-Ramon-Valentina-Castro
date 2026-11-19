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

from final.confirmation_final import cases
from final.gemini_judge_client import ApiFailure
from final.hydrogen_confirmation13 import (
    ConfirmationGenerator, verify_checkpoint, verify_approval, register_confirmation,
)
from final.hydrogen_paid12 import POLICY as POLICY12
from final.prepare_eval_final import canonical_hash
from final.tests.test_hydrogen_judge import config, Transport
from final.tests import test_hydrogen_paid12 as paid12_tests

ROOT = Path(__file__).resolve().parents[2]


class Confirmation13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checkpoint = verify_checkpoint(ROOT)

    def drive(self, folder):
        paid12_tests.Paid12Tests.drive(self, folder)
        (Path(folder)/'hydrogen_paid_12.started.json').write_text(json.dumps({
            'policy': POLICY12, 'generation_config_sha256': canonical_hash(config()),
            'financial_checkpoint_archive_sha256': '67b8992833627382fcc20e5c9def59ebfffec6084c2a7fb813c26835d4ec3ac2'}), encoding='utf-8')

    def client(self, folder, transport=None):
        fake = transport or Transport()
        def send(method, path, body):
            return self.checkpoint['metadata']['model_preflight'] if method == 'GET' else fake(method, path, body)
        return ConfirmationGenerator('FAKE', config(), Path(folder)/'api_budget_ledger.json', Path(folder)/'calls.jsonl',
            checkpoint=self.checkpoint, confirmed_paid_project=True, exclusive_project_use=True,
            transport=send, now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc), clock=lambda: 0, sleeper=lambda _: None)

    def test_previous_gates_and_all_human_approvals(self):
        self.assertEqual(len(self.checkpoint['budget_snapshot']['requests']), 45)
        self.assertEqual(len(verify_approval(ROOT)['approved_ids']), 12)

    def test_old_marker_preservation_and_exclusive_new_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            old = {p.name: p.read_bytes() for p in Path(temp).iterdir()}
            register_confirmation(temp, config(), self.checkpoint)
            with self.assertRaises(FileExistsError): register_confirmation(temp, config(), self.checkpoint)
            for name, raw in old.items(): self.assertEqual((Path(temp)/name).read_bytes(), raw)

    def test_missing_paid_marker_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            (Path(temp)/'hydrogen_paid_12.started.json').unlink()
            with self.assertRaises(ApiFailure): self.client(temp)

    def test_503_no_retry_preserves_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            client = self.client(temp, Transport(error=ApiFailure('api_http_error', 503)))
            client.preflight()
            with self.assertRaises(ApiFailure): client.generate('s', 'u')
            self.assertEqual(client.generation_calls, 1)
            self.assertEqual(client.ledger.used_or_reserved(), Decimal('4.6944825'))

    def test_full_runner_success_remains_pending_semantic_audit(self):
        self.run_scenario('pass', 12, True)

    def test_runner_stops_on_first_bad_accepted_without_resampling(self):
        self.run_scenario('bad_accepted', 2, False)

    def test_runner_stops_on_transport_failure(self):
        self.run_scenario('503', 1, False)

    def run_scenario(self, mode, calls_expected, passes):
        from final import run_hydrogen_confirmation13 as runner
        from m3.judge import evidence_payload
        expected = {canonical_hash(evidence_payload(c['record'])): (5 if c['group'] == 'good' else 2) for c in cases()}
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'drive'
            folder.mkdir()
            self.drive(folder)
            clients = []
            def fake(method, path, body):
                if path.endswith(':generateContent'):
                    payload = json.loads(body['contents'][0]['parts'][0]['text'])
                    self.assertNotIn('expected_score_range', payload)
                    self.assertNotIn('group', payload)
                    if mode == '503': raise ApiFailure('api_http_error', 503)
                    score = 5 if mode == 'bad_accepted' else expected[canonical_hash(payload)]
                    return Transport(score=score)(method, path, body)
                return Transport()(method, path, body)
            def factory(key, cfg, ledger_path, audit_path, **kwargs):
                def send(method, path, body):
                    return self.checkpoint['metadata']['model_preflight'] if method == 'GET' else fake(method, path, body)
                client = ConfirmationGenerator(key, cfg, ledger_path, audit_path, **kwargs, transport=send,
                    now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc), clock=lambda: 0, sleeper=lambda _: None)
                clients.append(client)
                return client
            def run(output):
                argv = ['confirmation13', '--output', str(output), '--budget-dir', str(folder),
                        '--confirm-paid-project', '--confirm-exclusive-budget-use']
                with patch.object(sys, 'argv', argv), patch.dict('os.environ', {'GEMINI_API_KEY': 'FAKE', 'WANDB_API_KEY': ''}), \
                     patch.object(runner, 'ConfirmationGenerator', side_effect=factory), contextlib.redirect_stdout(io.StringIO()):
                    runner.main()
            output = Path(temp)/'results'
            run(output)
            meta = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['generation_http_calls'], calls_expected)
            self.assertEqual(meta['confirmation_gate_passed'], passes)
            self.assertFalse(meta['judge_validated_for_final'])
            self.assertFalse(meta['final_gold_loaded'])
            self.assertLess(Decimal(meta['estimated_or_reserved_total_usd']), Decimal(5))
            with self.assertRaises(SystemExit): run(Path(temp)/'repeat')
            self.assertEqual(sum(c.generation_calls for c in clients), calls_expected)
