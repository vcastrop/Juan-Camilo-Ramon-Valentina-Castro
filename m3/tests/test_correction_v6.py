import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from correction_v6 import ContrastJudge,generate_v6,parse_v6,ANSWER_V6
from calibration_v1 import calibration_cases,evaluate_calibration
from run_correction_v6 import load_replay,FrozenRetriever


class Generator:
    def __init__(self,outputs):
        self.outputs=iter(outputs);self.calls=[]
    def generate(self,system,user):
        self.calls.append((system,json.loads(user)))
        return next(self.outputs)


def judgment(answer='wrong',score=4):
    return json.dumps({'respuesta_citada':answer,'contraste':'Hay una discrepancia.','puntaje':score,'razon':'Revisar sustento.'})


class CorrectionTests(unittest.TestCase):
    def test_score_not_replaced_or_retried_on_wrong_quote(self):
        case=next(c for c in calibration_cases() if c['id']=='wrong_2')
        g=Generator([judgment('12000',4)])
        result=ContrastJudge(g).evaluate(case['record'])
        self.assertEqual(result['score'],4)
        self.assertFalse(result['quoted_answer_matches'])
        self.assertFalse(result['score_adjusted'])
        self.assertEqual(len(g.calls),1)

    def test_no_gold_or_expected_in_judge(self):
        record=calibration_cases()[0]['record'] | {'expected':'SECRET','correct':True,'expected_range_for_review':[1,2]}
        g=Generator([judgment()]);ContrastJudge(g).evaluate(record)
        sent=json.dumps(g.calls[0][1])
        for forbidden in ['SECRET','expected_range','correct']:
            self.assertNotIn(forbidden,sent)

    def test_format_retry_only_and_missing_score(self):
        g=Generator(['not json','still invalid'])
        result=ContrastJudge(g).evaluate(calibration_cases()[0]['record'])
        self.assertIsNone(result['score']);self.assertEqual(len(result['attempts']),2)

    def test_parser_rejects_ambiguous_score_and_missing_reason(self):
        for raw in ['{"respuesta_citada":"x","contraste":"x","puntaje":4,"puntaje":1,"razon":"x"}',
                    '{"respuesta_citada":"x","contraste":"x","puntaje":true,"razon":"x"}',
                    '{"respuesta_citada":"x","contraste":"","puntaje":4,"razon":"x"}']:
            with self.assertRaises(ValueError):parse_v6(raw)

    def test_semantically_bad_answer_is_preserved(self):
        # Valid JSON does not get converted to an abstention by a hidden rule.
        output={'respuesta':'Auditoría aprobada','explicacion':'Lo dice el estado','citas':['x'],'abstencion':False}
        g=Generator([json.dumps(output)])
        result=generate_v6(g,'¿Qué concluyó la auditoría?',[{'doc_id':'d','chunk_id':'x','text':'Estado: Aprobado'}])
        self.assertEqual(result['output'],output)
        self.assertEqual(g.calls[0][0],ANSWER_V6)
        self.assertEqual(len(g.calls),1)

    def test_real_replay_preserved_and_three_key_failures_present(self):
        rows,sha=load_replay()
        self.assertEqual(len(rows),32);self.assertEqual(len(sha),64)
        a={r['development_index']:r for r in rows if r['variant']=='agent_v5'}
        self.assertFalse(a[7]['output']['abstencion'])
        self.assertIn('auditor',a[7]['output']['respuesta'])
        self.assertFalse(a[6]['output']['abstencion'])
        self.assertEqual(a[4]['tool_trace'][0]['tool_result']['absolute_difference_cop'],'75233920')

    def test_calibration_48_calls_unchanged_cases(self):
        g=Generator([judgment()]*48);emitted=[]
        rows=evaluate_calibration(g,emitted.append,judge_factory=ContrastJudge)
        self.assertEqual(len(rows),48);self.assertEqual(len(emitted),48)
        self.assertTrue(all(r['judgement']['score']==4 for r in rows))

    def test_frozen_retrieval_cannot_change_question(self):
        retriever=FrozenRetriever('q',[{'chunk_id':'x'}])
        self.assertEqual(len(retriever.search('q',3)),1)
        with self.assertRaises(ValueError):retriever.search('other',3)


if __name__=='__main__':unittest.main()
