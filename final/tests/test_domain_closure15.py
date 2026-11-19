import json
from pathlib import Path
import unittest
from unittest.mock import patch

from final import domain_closure15 as closure
from final.domain_scorecard14 import build as previous

ROOT = Path(__file__).resolve().parents[2]


class DomainClosure15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = closure.build(ROOT)

    def test_original_doubt_preserved_and_explicit_no_applied(self):
        r = self.result['review46_receipt']
        key = 'qa_no_rag_fp16/m3_011'
        self.assertEqual(r['original_parsed_review']['annotations'][key]['criteria']['Abstención adecuada'], 'DUDOSO')
        self.assertEqual(r['effective_review']['annotations'][key]['criteria']['Abstención adecuada'], 'NO')
        self.assertFalse(r['original_file_modified'])
        self.assertFalse(r['llm_scores_created_or_adjusted'])

    def test_all_110_resolved_with_exact_counts(self):
        counts = {t['profile']: t['domain_pass_count'] for t in self.result['tables']}
        self.assertEqual(counts, {'qa_no_rag_fp16': 3, 'm3_text_fp16': 7, 'integrated_fp16': 16,
                                  'integrated_nf4': 11, 'integrated_no_tool_fp16': 15})
        self.assertEqual(self.result['pending_semantic_keys'], [])
        self.assertEqual(self.result['semantic_coverage'], {'direct_signed_rows': 90, 'exact_content_transfers': 20, 'complete_rows': 110})

    def test_historical_results_and_raw_scores_not_changed(self):
        old = previous(ROOT)
        for profile, rows in old['domain_details'].items():
            new = {r['id']: r for r in self.result['domain_details'][profile]}
            for r in rows:
                self.assertEqual(r['raw_judge_score'], new[r['id']]['raw_judge_score'])
                if r['domain_pass'] is not None:
                    self.assertEqual(r['domain_pass'], new[r['id']]['domain_pass'])
        self.assertEqual(self.result['efficiency_decision'], old['efficiency_decision'])
        self.assertEqual(self.result['network_requests_made'], 0)

    def test_new_critical_annotations_recorded_not_repaired(self):
        m3 = {r['id']: r for r in self.result['domain_details']['m3_text_fp16']}
        ablation = {r['id']: r for r in self.result['domain_details']['integrated_no_tool_fp16']}
        self.assertEqual(m3['m3_012']['critical_failures'], ['unsupported_audit_or_fraud_claim'])
        self.assertEqual(ablation['m3_007']['critical_failures'], ['central_numeric_error'])
        self.assertFalse(ablation['m3_007']['domain_pass'])

    def test_blanket_abstention_not_confused_with_visual_capability(self):
        rows = {r['id']: r for r in self.result['domain_details']['qa_no_rag_fp16']}
        self.assertEqual(rows['vis_01']['raw_judge_score'], 5)
        self.assertFalse(rows['vis_01']['domain_pass'])
        self.assertTrue(rows['vis_08_blank']['domain_pass'])
        self.assertIn('trivial', rows['vis_08_blank']['semantic_observations'])

    def test_forged_si_closure_is_rejected(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == 'chat_closure.json':
                data = json.loads(text)
                data['confirmed_value'] = 'SI'
                return json.dumps(data)
            return text
        with patch.object(Path, 'read_text', read), self.assertRaisesRegex(ValueError, 'adjudication'):
            closure.receipt(ROOT, previous(ROOT))

    def test_saved_complete_scorecard_reproduces(self):
        saved = json.loads((ROOT/'final/evidence/domain_review46/scorecard_complete.json').read_text(encoding='utf-8'))
        self.assertEqual(saved, self.result)
