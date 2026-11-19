import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import contextlib
import io
import sys
from unittest.mock import patch
from datetime import datetime, timezone
from decimal import Decimal

from final.gemini_judge_client import ApiFailure
from final.hydrogen_paid12 import PaidGenerator, verify_checkpoint, register_paid
from final.hydrogen_recovery11 import POLICY as POLICY11
from final.prepare_eval_final import canonical_hash
from final.tests.test_hydrogen_judge import config, budget, Transport

ROOT = Path(__file__).resolve().parents[2]


class Paid12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checkpoint = verify_checkpoint(ROOT)

    def drive(self, temp):
        budget(temp, self.checkpoint['base_drive'])
        for name in ['hydrogen_calibration_candidate_1.started.json', 'hydrogen_calibration_resume_1.started.json']:
            (Path(temp)/name).write_text(json.dumps({'config_sha256': canonical_hash(config()),
                'checkpoint_sha256': self.checkpoint['archive_sha256']}), encoding='utf-8')
        (Path(temp)/'hydrogen_calibration_resume_2.started.json').write_text(json.dumps({
            'config_sha256': canonical_hash(config()), 'policy': POLICY11,
            'financial_checkpoint_archive_sha256': '4e8d9f311ba4fdf83235cae8e69ba851b9161d5853e7613ddc657ce8039b9494'}), encoding='utf-8')

    def client(self, temp, error=None, score=2, **kwargs):
        fake = Transport(error=error, score=score)
        def send(method, path, body):
            if method == 'GET':
                return self.checkpoint['metadata']['model_preflight']
            return fake(method, path, body)
        params = dict(confirmed_paid_project=True, exclusive_project_use=True,
                      transport=send, now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc),
                      clock=lambda: 0, sleeper=lambda _: None)
        params.update(kwargs)
        client = PaidGenerator('FAKE', config(), Path(temp)/'api_budget_ledger.json',
                               Path(temp)/'calls.jsonl', checkpoint=self.checkpoint, **params)
        client.preflight()
        return client

    def test_eight_prior_entries_and_one_valid_score(self):
        self.assertEqual(len(self.checkpoint['budget_snapshot']['requests']), 8)
        self.assertEqual(self.checkpoint['saved_rows'][0]['judgement']['score'], 2)

    def test_paid_and_exclusive_budget_confirmation_required(self):
        for kw in [dict(confirmed_paid_project=False), dict(exclusive_project_use=False)]:
            with tempfile.TemporaryDirectory() as temp:
                self.drive(temp)
                with self.assertRaises(ApiFailure): self.client(temp, **kw)

    def test_price_expiry_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            with self.assertRaises(ApiFailure):
                self.client(temp, now_utc=datetime(2026, 11, 21, tzinfo=timezone.utc))

    def test_missing_marker_and_changed_ledger_block(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            path = Path(temp)/'hydrogen_calibration_resume_2.started.json'
            path.unlink()
            with self.assertRaises(ApiFailure): self.client(temp)
            self.drive(temp)
            path = Path(temp)/'api_budget_ledger.json'
            data = json.loads(path.read_text())
            data['requests'].pop(next(iter(data['requests'])))
            path.write_text(json.dumps(data))
            with self.assertRaises(ApiFailure): self.client(temp)

    def test_exclusive_marker_preserves_prior_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            before = {p.name: p.read_bytes() for p in Path(temp).iterdir()}
            register_paid(temp, config(), self.checkpoint)
            with self.assertRaises(FileExistsError): register_paid(temp, config(), self.checkpoint)
            for name, raw in before.items(): self.assertEqual((Path(temp)/name).read_bytes(), raw)

    def test_503_no_retry_and_unknown_cost_kept(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            client = self.client(temp, error=ApiFailure('api_http_error', 503))
            with self.assertRaises(ApiFailure): client.generate('s', 'u')
            self.assertEqual(client.generation_calls, 1)
            self.assertEqual(client.retry_count, 0)
            self.assertEqual(client.ledger.used_or_reserved(), Decimal('4.3138725'))

    def test_wrong_valid_score_not_corrected_and_never_attests_free(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            client = self.client(temp, score=4)
            self.assertEqual(json.loads(client.generate('s', 'u'))['puntaje'], 4)
            self.assertFalse(client.last_generation['free_project_attested'])
            journal = (Path(temp)/'calls.jsonl').read_text()
            self.assertNotIn('"free_project_attested": true', journal)
            self.assertNotIn('PRIVATE', journal)

    def test_pending_payload_unchanged(self):
        from final.calibration_final import cases
        from final.judge_final import FinalJudge
        from final.reasoning_calibration import request_seed
        from m3.judge import evidence_payload
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            client = self.client(temp)
            client.set_request_seed(request_seed('attribution_good', 42))
            record = next(c['record'] for c in cases() if c['id'] == 'attribution_good')
            body = client.request_body(FinalJudge(client).system, json.dumps(evidence_payload(record), ensure_ascii=False))
            digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            self.assertEqual(digest, '9f5a82938ae3efda77aea6c6c53045266802da363892446302056361b37ac1b5')

    def test_insufficient_margin_prevents_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            self.drive(temp)
            client = self.client(temp)
            client.ledger.reserve('1.00')
            with self.assertRaises(ApiFailure): client.generate('s', 'u')
            self.assertEqual(client.generation_calls, 0)

    def test_runner_503_preserves_score_snapshot_and_blocks_repeat(self):
        from final import run_hydrogen_paid12 as runner
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'drive'
            folder.mkdir()
            self.drive(folder)
            original = {p.name: p.read_bytes() for p in folder.glob('*.started.json')}
            clients = []
            def factory(key, cfg, ledger_path, audit_path, **kwargs):
                fake = Transport(error=ApiFailure('api_http_error', 503))
                def transport(method, path, body):
                    return self.checkpoint['metadata']['model_preflight'] if method == 'GET' else fake(method, path, body)
                client = PaidGenerator(key, cfg, ledger_path, audit_path, **kwargs,
                    transport=transport, now_utc=datetime(2026, 11, 19, tzinfo=timezone.utc),
                    clock=lambda: 0, sleeper=lambda _: None)
                clients.append(client)
                return client
            def run(output):
                argv = ['paid12', '--output', str(output), '--budget-dir', str(folder),
                        '--confirm-paid-project', '--confirm-exclusive-budget-use']
                with patch.object(sys, 'argv', argv), patch.dict('os.environ', {'GEMINI_API_KEY': 'FAKE', 'WANDB_API_KEY': ''}), \
                     patch.object(runner, 'PaidGenerator', side_effect=factory), contextlib.redirect_stdout(io.StringIO()):
                    runner.main()
            output = Path(temp)/'result'
            run(output)
            meta = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            rows = [json.loads(s) for s in (output/'raw_judgements.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(meta['generation_http_calls'], 1)
            self.assertEqual(meta['estimated_or_reserved_total_usd'], '4.3138725')
            self.assertFalse(meta['judge_validated_for_final'])
            self.assertFalse(meta['free_project_attested'])
            self.assertEqual(rows[0]['judgement'], self.checkpoint['saved_rows'][0]['judgement'])
            self.assertIsNone(rows[1]['judgement']['score'])
            for name, raw in original.items(): self.assertEqual((folder/name).read_bytes(), raw)
            with self.assertRaises(SystemExit): run(Path(temp)/'second')
            self.assertEqual(sum(c.generation_calls for c in clients), 1)
