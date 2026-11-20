from pathlib import Path
import tempfile
import unittest

from final.visual21_receipt import receipt

ROOT=Path(__file__).resolve().parents[2]
SIGNED=ROOT/'final/evidence/visual21_received/REVISION_VISUAL_21.md'


class Receipt21Tests(unittest.TestCase):
    def test_received_human_review_is_complete_but_not_judge_or_domain(self):
        result=receipt(SIGNED)
        self.assertEqual(result['human_cases'],10)
        self.assertTrue(result['judge_evaluation_pending'])
        self.assertIsNone(result['domain_rate'])
        self.assertEqual(result['reviews'][6]['signed_criteria']['Fallos críticos'],'NINGUNO')
        self.assertIn('nunca recibió la inyección',result['reviews'][6]['semantic_observations'])

    def test_changed_saved_evidence_is_rejected(self):
        text=SIGNED.read_text(encoding='utf-8').replace('60600750','60600751',1)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'changed.md';path.write_text(text,encoding='utf-8')
            with self.assertRaises(ValueError):receipt(path)

    def test_unsigned_template_is_rejected(self):
        with self.assertRaises(ValueError):receipt(ROOT/'final/evidence/evaluation21_review/REVISION_VISUAL_21.md')
