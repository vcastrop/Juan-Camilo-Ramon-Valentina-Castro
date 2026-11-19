import copy,json,unittest
from pathlib import Path
from final.human_response_review import load_received,parse,analyze

ROOT=Path(__file__).resolve().parents[2]


class ReviewTests(unittest.TestCase):
    def test_actual_review_keeps_eight_open_items_and_no_grades(self):
        review,result=load_received()
        self.assertEqual(len(review['annotations']),44);self.assertEqual(result['records_with_doubts'],8)
        self.assertFalse(result['llm_grades_created']);self.assertIsNone(result['domain_rate'])
        self.assertTrue(result['nf4_deployment_veto'])
        self.assertEqual(result['new_confirmed_critical_failures_nf4'][0]['id'],'m3_001')
        self.assertEqual(len(result['human_control_regressions']),2)

    def test_no_invented_critical_codes_or_silent_omissions(self):
        manifest=json.loads((ROOT/'final/eval/review_comparison02/manifest.json').read_text(encoding='utf-8'))
        protocol=json.loads((ROOT/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
        text=(ROOT/'final/evidence/human_response_review_01/original_review.md').read_text(encoding='utf-8-sig')
        bad=text.replace('Fallos críticos: NINGUNO','Fallos críticos: NEW_CODE',1)
        with self.assertRaises(ValueError):parse(bad,manifest,protocol)
        with self.assertRaises(ValueError):parse(text.replace('Respuesta respaldada: SI','Respuesta respaldada: PENDIENTE',1),manifest,protocol)
