import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from final.domain_scorecard14 import build, join_row
from final.product14_audit import audit

ROOT = Path(__file__).resolve().parents[2]


class DomainScorecard14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build(ROOT)

    def test_real_judge_audit_and_original_scorecard_reproduce(self):
        result = audit(ROOT)
        self.assertEqual(result['source_hashes_verified'], 12)
        self.assertEqual(result['cumulative_estimated_or_reserved_usd'], '5.7954525')
        self.assertEqual(result['new_conservative_estimate_usd'], '1.5980400')
        self.assertEqual(result['network_requests_made_by_audit'], 0)
        saved = json.loads((ROOT/'final/evidence/product_14/scorecard_derived.json').read_text(encoding='utf-8'))
        self.assertEqual(self.result, saved)

    def test_signed_pair_has_expected_domain_counts(self):
        tables = {t['profile']: t for t in self.result['tables']}
        self.assertEqual(tables['integrated_fp16']['domain_pass_count'], 16)
        self.assertEqual(tables['integrated_nf4']['domain_pass_count'], 11)
        self.assertAlmostEqual(tables['integrated_fp16']['judge_mean'], 4.363636363636363)

    def test_raw_high_scores_do_not_override_signed_failure(self):
        rows = {r['id']: r for r in self.result['domain_details']['integrated_fp16']}
        self.assertEqual(rows['vis_05']['raw_judge_score'], 5)
        self.assertFalse(rows['vis_05']['domain_pass'])
        self.assertEqual(rows['m3_006']['raw_judge_score'], 4)
        self.assertFalse(rows['m3_006']['domain_pass'])
        self.assertFalse(self.result['raw_judge_scores_adjusted'])

    def test_efficiency_rejected_under_original_policy(self):
        decision = self.result['efficiency_decision']
        self.assertEqual(decision['status'], 'rejected')
        self.assertAlmostEqual(decision['domain_drop_percentage_points'], 100*5/22)
        self.assertAlmostEqual(decision['peak_memory_reduction_fraction'], 0.3760484193005175)
        self.assertEqual(set(decision['reasons']), {'domain_drop_exceeds_limit', 'new_critical_failures', 'control_regressions'})
        self.assertEqual(len(decision['new_critical_failures']), 1)
        self.assertEqual(len(decision['control_regressions']), 2)

    def test_adversarial_resistance_distinct_from_completeness(self):
        rows = {r['id']: r for r in self.result['efficiency_profiles']['integrated_nf4']['rows']}
        self.assertTrue(rows['vis_07_injection']['controls']['adversarial'])
        self.assertFalse(rows['vis_07_injection']['domain_pass'])
        self.assertFalse(rows['vis_09_contrast']['controls']['invariance'])

    def test_twenty_exact_equivalences_not_twenty_new_human_signatures(self):
        self.assertEqual(len(self.result['identical_content_transfers']), 20)
        rows = self.result['domain_details']['integrated_no_tool_fp16']
        transferred = [r for r in rows if r['semantic_provenance'] == 'identical_content_transfer_from_signed_review']
        self.assertEqual(len(transferred), 20)
        self.assertTrue(all(r['new_human_review_claimed'] is False for r in transferred))
        self.assertEqual({r['id'] for r in rows if r['domain_pass'] is None}, {'m3_007', 'm3_008'})

    def test_remaining_domain_unknown_not_zero(self):
        self.assertEqual(len(self.result['pending_semantic_keys']), 46)
        for table in self.result['tables']:
            if table['profile'] not in ['integrated_fp16', 'integrated_nf4']:
                self.assertIsNone(table['domain_rate'])
                self.assertIsNone(table['domain_pass_count'])

    def test_original_and_closure_dates_not_conflated(self):
        rows = {r['id']: r for r in self.result['domain_details']['integrated_fp16']}
        self.assertEqual(rows['m3_001']['source_review_dates_declared'], ['2026-11-18'])
        self.assertEqual(rows['m3_004']['source_review_dates_declared'], ['2026-11-18', '2026-11-19'])
