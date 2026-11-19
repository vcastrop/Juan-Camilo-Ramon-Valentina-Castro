import json,unittest
from pathlib import Path
from final.comparison02_audit import audit
from final.tool_usage import metrics
from final.prepare_eval_final import canonical_hash

ROOT=Path(__file__).resolve().parents[2]


class AuditTests(unittest.TestCase):
    def test_router_is_not_successful_tool(self):
        event={'decision':{'action':'answer'},'tool_result':None}
        data=metrics({'tool_trace':[event]})
        self.assertTrue(data['router_used']);self.assertFalse(data['tool_requested'])
        self.assertFalse(data['tool_result_recorded']);self.assertFalse(data['tool_success'])

    def test_failed_or_blocked_tool_is_not_success(self):
        data=metrics({'tool_trace':[{'decision':{'action':'tool'},'tool_result':{'ok':False}}]})
        self.assertTrue(data['tool_requested']);self.assertTrue(data['tool_result_recorded']);self.assertFalse(data['tool_success'])
        self.assertFalse(metrics({'tool_trace':None})['router_used'])

    def test_recalculation_matches_preserved_derived_report(self):
        recalculated=audit()
        saved=json.loads((ROOT/'final/evidence/comparison_02/recalculated.json').read_text(encoding='utf-8'))
        self.assertEqual(recalculated,saved)
        self.assertEqual(recalculated['corrected_tool_usage']['m3_text_fp16']['router_cases'],12)
        self.assertEqual(recalculated['corrected_tool_usage']['m3_text_fp16']['successful_tool_cases'],2)
        self.assertGreater(recalculated['memory_reduction_fraction'],.20)
        self.assertFalse(recalculated['judge_validated'])
        self.assertTrue(all(t['domain_rate'] is None and t['judge_mean'] is None for t in recalculated['tables']))

    def test_review_has_44_items_but_no_human_verdicts(self):
        folder=ROOT/'final/eval/review_comparison02'
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest),44);self.assertEqual(len({r['review_key'] for r in manifest}),44)
        self.assertEqual(canonical_hash(manifest),meta['manifest_canonical_sha256'])
        self.assertFalse(meta['human_verdicts_created']);self.assertFalse(meta['model_judge_grades_created'])
        self.assertEqual(meta['status'],'human_review_pending')
        review=(folder/'REVISION_RESPUESTAS.md').read_text(encoding='utf-8')
        self.assertEqual(review.count('Respuesta respaldada: PENDIENTE'),44)


if __name__=='__main__':unittest.main()
