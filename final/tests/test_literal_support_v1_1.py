import copy,json,unittest
from pathlib import Path
from final.calibration_final import cases,schedule
from final.judge_literal import LiteralJudge
from final.literal_calibration import PILOT_IDS
from final.literal_support_v1_1 import ContinuedLiteralJudge,evaluate_saved,load_previous,pilot_summary,support_issues,validate_config

ROOT=Path(__file__).resolve().parents[2]


class LiteralSupportCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.rows,self.meta=load_previous(ROOT)
        self.record=next(c['record'] for c in cases() if c['id']=='citation_bad')
        j=self.rows[-1]['judgement']
        self.obj={'verificaciones':copy.deepcopy(j['checks']),'soportes':copy.deepcopy(j['supports']),
                  'puntaje':j['score'],'razon':j['reason']}

    def test_seven_saved_scores_and_model_outputs_unchanged(self):
        self.assertEqual([r['judgement']['score'] for r in self.rows],[5,2,1,4,2,2,2])
        self.assertTrue(all(not r['provenance']['regenerated'] for r in self.rows))
        self.assertEqual(self.rows[-1]['judgement']['historical_internal_inconsistencies'],['respuesta:unknown_or_uncited_chunk'])
        self.assertEqual(self.rows[-1]['judgement']['internal_inconsistencies'],[])

    def test_full_pilot_still_incomplete(self):
        self.assertTrue(pilot_summary(self.rows,PILOT_IDS[:7])['pilot_passed'])
        summary=pilot_summary(self.rows,PILOT_IDS)
        self.assertFalse(summary['pilot_passed'])
        self.assertEqual(summary['unexecuted_ids'],PILOT_IDS[7:])

    def test_diagnostic_can_use_available_uncited_literal(self):
        self.assertEqual(support_issues(self.obj,self.record),[])
        self.assertEqual(self.record['output']['citas'],['OTHER::nota'])

    def test_cannot_use_uncited_fragment_to_approve_answer(self):
        self.obj['verificaciones']['respuesta']='respaldada'
        self.assertIn('respuesta:uncited_support_not_diagnostic',support_issues(self.obj,self.record))
        self.obj['verificaciones']['respuesta']='contradicha'
        self.obj['verificaciones']['citas']='respaldan'
        self.assertIn('respuesta:uncited_support_not_diagnostic',support_issues(self.obj,self.record))

    def test_unknown_and_nonliteral_quotes_always_rejected(self):
        self.obj['soportes'][0]['chunk_id']='UNKNOWN'
        self.assertIn('respuesta:unknown_chunk',support_issues(self.obj,self.record))
        self.obj['soportes'][0]['chunk_id']='SYNTH::ficha'
        self.obj['soportes'][0]['cita_literal']='Entidad: Agencia Inventada'
        self.assertIn('respuesta:nonliteral_quote',support_issues(self.obj,self.record))

    def test_score_not_replaced_even_if_high_and_inconsistent(self):
        j=copy.deepcopy(self.rows[-1]['judgement']);j['score']=5
        result=evaluate_saved(j,self.record)
        self.assertEqual(result['score'],5)
        self.assertIn('high_score_despite_reported_defect',result['internal_inconsistencies'])
        self.assertFalse(result['score_adjusted'])

    def test_prompt_and_generation_contract_identical(self):
        self.assertEqual(ContinuedLiteralJudge(None).system,LiteralJudge(None).system)
        cfg=json.loads((ROOT/'final/judge_continuation_config.json').read_text(encoding='utf-8'))
        validate_config(cfg)
        cfg['max_new_tokens']=8192
        with self.assertRaises(ValueError):validate_config(cfg)

    def test_remaining_agenda_has_no_repeated_saved_call(self):
        done={(r['condition'],r['id']) for r in self.rows}
        remaining=[item for item in schedule() if item not in done]
        self.assertEqual(len(remaining),31)
        self.assertEqual(len(set(remaining)|done),38)
        self.assertFalse(set(remaining)&done)


if __name__=='__main__':unittest.main()
