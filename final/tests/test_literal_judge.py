import copy,json,unittest
from final.calibration_final import cases,verbose,schedule
from final.judge_literal import LiteralJudge,collapse_exact_repetition,normalized_record,parse_literal,support_issues
from final.literal_calibration import validate_config,PILOT_IDS,pilot_summary,full_summary
from final.tests.test_reasoning_judge import FakeGenerator,verdict
from final.tests import test_reasoning_judge as previous_tests
from pathlib import Path


def output(score=5):
    obj=json.loads(verdict(score))
    obj['soportes']=[{'componente':c,'campo':'Modalidad de contratación','chunk_id':'SYNTH::ficha',
                    'cita_literal':'Modalidad de contratación: Mínima cuantía'} for c in ['respuesta','explicacion']]
    return obj


class LiteralJudgeTests(unittest.TestCase):
    def test_exact_whole_blocks_only(self):
        for text in ['A. B.','No es fraude.','85000 COP','á\nβ']:
            self.assertEqual(collapse_exact_repetition(' '.join([text]*4)),text)
        for text in ['No. No es fraude.','85000 COP 850000 COP','A A B','A. A!','a  a','']:
            self.assertEqual(collapse_exact_repetition(text),text)

    def test_verbose_and_concise_mitigated_packets_equal(self):
        record=cases()[0]['record'];v=verbose(record)
        self.assertEqual(normalized_record(v,True)[0],record)
        self.assertEqual(normalized_record(v,False)[0],v)
        self.assertNotEqual(v,record)
        self.assertEqual(record,cases()[0]['record'])

    def test_sources_citations_and_gold_never_normalized(self):
        record=copy.deepcopy(cases()[0]['record']);record['contexts'][0]['text']='A A A A'
        record['expected']='SECRET'
        gen=FakeGenerator([json.dumps(output())]);LiteralJudge(gen).evaluate(record)
        packet=gen.calls[0]
        self.assertNotIn('expected',packet)
        self.assertIn('A A A A',json.dumps(packet))

    def test_fabricated_quote_keeps_score_and_no_semantic_retry(self):
        obj=output(5);obj['soportes'][0]['cita_literal']='Modalidad de contratación: Fabricada'
        gen=FakeGenerator([json.dumps(obj)])
        result=LiteralJudge(gen).evaluate(cases()[0]['record'])
        self.assertEqual(result['score'],5)
        self.assertIn('respuesta:nonliteral_quote',result['internal_inconsistencies'])
        self.assertEqual(len(gen.calls),1)
        self.assertFalse(result['score_adjusted'])

    def test_wrong_chunk_field_and_missing_evidence(self):
        record=cases()[0]['record'];obj=output()
        self.assertEqual(support_issues(obj,record),[])
        obj['soportes'][0]['chunk_id']='OTHER::nota'
        self.assertIn('respuesta:unknown_or_uncited_chunk',support_issues(obj,record))
        obj=output();obj['soportes'][0]['campo']='Objeto'
        self.assertIn('respuesta:field_not_in_quote',support_issues(obj,record))
        obj=output();obj['soportes'][0].update(campo=None,chunk_id=None,cita_literal=None)
        self.assertIn('respuesta:supported_without_literal_evidence',support_issues(obj,record))

    def test_actual_support_schema_not_optional(self):
        with self.assertRaises(ValueError):parse_literal(verdict())
        obj=output();obj['soportes'][1]=copy.deepcopy(obj['soportes'][0])
        with self.assertRaises(ValueError):parse_literal(json.dumps(obj))

    def test_literal_is_not_claim_of_semantic_entailment(self):
        # The validator does not infer that the field answers the question.
        obj=output();obj['soportes'][0].update(campo='Tipo de contrato',cita_literal='Tipo de contrato: Compraventa')
        self.assertEqual(support_issues(obj,cases()[0]['record']),[])

    def test_format_retry_only_and_incomplete_not_retried(self):
        gen=FakeGenerator(['bad',json.dumps(output())])
        self.assertEqual(LiteralJudge(gen).evaluate(cases()[0]['record'])['score'],5)
        self.assertEqual(len(gen.calls),2)
        gen=FakeGenerator([''],{'thinking_closed':False})
        self.assertIsNone(LiteralJudge(gen).evaluate(cases()[0]['record'])['score'])
        self.assertEqual(len(gen.calls),1)

    def test_fixed_config_and_expanded_pilot(self):
        config=json.loads((Path(__file__).resolve().parents[1]/'judge_literal_config.json').read_text(encoding='utf-8'))
        validate_config(config);self.assertEqual(len(PILOT_IDS),9)
        config['temperature']=0.1
        with self.assertRaises(ValueError):validate_config(config)

    def test_missing_support_recomputed_and_fails_gate(self):
        rows=previous_tests.ReasoningJudgeTests().ideal_rows()
        result=full_summary(rows)
        self.assertFalse(result['gate_passed'])
        self.assertTrue(result['inconsistent_judgements'])
        self.assertFalse(pilot_summary(rows[:1],PILOT_IDS)['pilot_passed'])


if __name__=='__main__':unittest.main()
