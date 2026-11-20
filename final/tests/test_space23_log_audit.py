from pathlib import Path
import json
import unittest

from final.audit_space23_logs import audit

ROOT=Path(__file__).resolve().parents[2]


class SpaceLogTests(unittest.TestCase):
    def test_ten_attempts_and_three_explained_rejections_not_model_failures(self):
        folder=ROOT/'final/evidence/space_ocr23_cpu'
        result=audit(folder/'container_smoke_original.txt')
        self.assertEqual(result,json.loads((folder/'events_audit.json').read_text(encoding='utf-8')))
        self.assertEqual(result['accepted_smoke_events'],7)
        self.assertEqual(result['rejected_input_events'],3)
        self.assertEqual(result['runtime_error_events'],0)
        self.assertIsNone(result['wandb_crash_cause'])
        self.assertFalse(result['monitoring_live_connection_verified'])
