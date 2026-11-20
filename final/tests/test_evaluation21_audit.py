import json
from pathlib import Path
import unittest

from final.evaluation21_audit import audit

ROOT=Path(__file__).resolve().parents[2]


class Audit21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=audit()

    def test_saved_scorecard_reproduces(self):
        self.assertEqual(self.result,json.loads((ROOT/'final/evidence/evaluation21_completed/scorecard.json').read_text(encoding='utf-8')))
        self.assertEqual(self.result['domain_pass_count'],18)
        self.assertAlmostEqual(self.result['judge_mean_1_5'],98/22)

    def test_bad_text_and_high_grade_disagreement_preserved(self):
        details={d['id']:d for d in self.result['domain_details']}
        self.assertEqual({k for k,v in details.items() if not v['domain_pass']},{'m3_003','m3_005','m3_006','m3_009'})
        self.assertEqual(details['m3_006']['raw_judge_score'],4)
        self.assertFalse(details['m3_006']['checks']['signed_semantic_criteria_pass'])
        self.assertEqual(details['m3_009']['raw_judge_score'],2)

    def test_accounting_and_public_deployment_not_invented(self):
        self.assertEqual(self.result['estimated_or_reserved_total_usd'],'5.9179725')
        self.assertEqual(self.result['incremental_estimated_usd'],'0.1225200')
        self.assertTrue(self.result['prior_167_entries_unchanged'])
        self.assertFalse(self.result['public_deployment_verified'])
        self.assertFalse(self.result['actual_invoice_verified'])
