import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from final import confirmation13_receipt as receipt
from final.prepare_closure_review import build

ROOT = Path(__file__).resolve().parents[2]


class ConfirmationReceiptTests(unittest.TestCase):
    def test_actual_receipt_has_no_human_signature_or_dispatch(self):
        result = receipt.receive(ROOT)
        self.assertFalse(result['judge_validated_for_final'])
        self.assertFalse(result['human_review_signed_by_assistant'])
        self.assertEqual(result['network_requests_made_by_receipt'], 0)
        self.assertEqual(result['margin_usd'], '0.8025875')
        self.assertEqual(result['spendable_before_last_required_reservation_usd'], '0.1881875')

    def test_changed_raw_note_rejected(self):
        files = receipt.read_archive(ROOT/'final/evidence/confirmation_13/original_results.zip', receipt.SHA13)
        rows = [json.loads(s) for s in files['raw_judgements.jsonl'].decode().splitlines()]
        rows[0]['judgement']['reason'] = 'Changed explanation'
        files['raw_judgements.jsonl'] = '\n'.join(json.dumps(r) for r in rows).encode()
        with patch.object(receipt, 'read_archive', return_value=files), self.assertRaisesRegex(ValueError, 'Raw note differs'):
            receipt.receive(ROOT)

    def test_changed_approval_rejected(self):
        files = receipt.read_archive(ROOT/'final/evidence/confirmation_13/original_results.zip', receipt.SHA13)
        meta = json.loads(files['metadata.json'])
        meta['approval_canonical_sha256'] = '0'*64
        files['metadata.json'] = json.dumps(meta).encode()
        with patch.object(receipt, 'read_archive', return_value=files), self.assertRaisesRegex(ValueError, 'Approval or rubric'):
            receipt.receive(ROOT)

    def test_builds_all_twelve_unsigned_motives_and_eight_open_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'review'
            package = build(ROOT, folder)
            motives = (folder/'REVISION_MOTIVOS_JUEZ.md').read_text(encoding='utf-8')
            doubts = (folder/'CIERRE_OCHO_DUDAS.md').read_text(encoding='utf-8')
            self.assertEqual(motives.count('Motivo aceptable: PENDIENTE'), 12)
            self.assertEqual(motives.count('## Calibración '), 38)
            self.assertIn('Motivos de calibración aceptables (conjunto): PENDIENTE', motives)
            self.assertEqual(doubts.count('Justificación de cierre: PENDIENTE'), 8)
            self.assertIn('Revisor/a: PENDIENTE', motives)
            self.assertIn('Revisor/a: PENDIENTE', doubts)
            self.assertEqual(doubts.count('## integrated_'), 8)
            self.assertEqual(len(list((folder/'imagenes').iterdir())), 2)
            with zipfile.ZipFile(package) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('REVISION_MOTIVOS_JUEZ.md', archive.namelist())
            with self.assertRaises(ValueError): build(ROOT, folder)
