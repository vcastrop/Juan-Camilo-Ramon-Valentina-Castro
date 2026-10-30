import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harness_qa import harness,token_f1,domain_traceability,validate_cases


def case(kind='factual'):
    return {'eval_id':'synthetic_1','input':'¿Qué entidad?','expected':'Entidad Norte',
            'criterion':'Identificar entidad','kind':kind,'source_ids':[] if kind=='unanswerable' else ['doc1']}


def record(answer='Entidad Norte',abstention=False):
    return {'output':{'respuesta':answer,'explicacion':'La ficha lo indica.',
                      'citas':['c1'],'abstencion':abstention},
            'contexts':[{'chunk_id':'c1','doc_id':'doc1','text':'Entidad: Norte','source_url':'synthetic://test'}]}


class System:
    def __init__(self,result=None,fail=False):self.result=result;self.fail=fail;self.inputs=[]
    def predict(self,question):
        self.inputs.append(question)
        if self.fail:raise RuntimeError('test failure')
        return self.result


class Judge:
    def __init__(self,score=2):self.score=score;self.inputs=[]
    def evaluate(self,record):
        self.inputs.append(record)
        return {'score':self.score,'reason':'Synthetic','attempts':[{'raw':'synthetic','parse_error':None,'generation_error':None}]}


class HarnessTests(unittest.TestCase):
    def test_f1_normalizes_accents_punctuation_whitespace(self):
        self.assertEqual(token_f1('MÍNIMA  cuantía!','minima cuantia'),1)
        self.assertEqual(token_f1('',''),0)
        self.assertAlmostEqual(token_f1('a a b','a b'),.8)

    def test_no_gold_sent_to_system_or_judge(self):
        s=System(record()|{'expected':'SECRET','correct':True});j=Judge()
        result=harness([case()],s,j)
        self.assertEqual(s.inputs,['¿Qué entidad?'])
        self.assertNotIn('expected',j.inputs[0]);self.assertNotIn('correct',j.inputs[0])
        self.assertEqual(result['scorecard']['judge']['mean_valid_only'],2)
        self.assertEqual(result['scorecard']['reference_token_f1_mean'],1)

    def test_wrong_answer_can_be_traceable_not_semantically_correct(self):
        r=record('Entidad Sur')
        self.assertTrue(domain_traceability(case(),r)['pass'])
        self.assertTrue(domain_traceability(case(),r)['semantic_review_required'])
        self.assertLess(token_f1(r['output']['respuesta'],case()['expected']),1)

    def test_unknown_or_duplicate_citations_rejected(self):
        r=record();r['output']['citas']=['missing']
        self.assertFalse(domain_traceability(case(),r)['pass'])
        r=record();r['contexts']*=2
        self.assertFalse(domain_traceability(case(),r)['pass'])

    def test_both_documents_required_for_calculation(self):
        c=case('calculation');c['source_ids']=['doc1','doc2']
        self.assertFalse(domain_traceability(c,record())['pass'])

    def test_unanswerable_requires_abstention_but_not_citation(self):
        r=record(abstention=True);r['output']['citas']=[];r['contexts']=[]
        self.assertTrue(domain_traceability(case('unanswerable'),r)['pass'])
        r['output']['abstencion']=False
        self.assertFalse(domain_traceability(case('unanswerable'),r)['pass'])

    def test_failed_system_remains_in_denominator(self):
        result=harness([case()],System(fail=True),None)
        s=result['scorecard'];self.assertEqual(s['total'],1)
        self.assertEqual(s['reference_token_f1_mean'],0)
        self.assertEqual(s['domain_traceability_rate'],0)
        self.assertEqual(s['system_error_count'],1)
        self.assertIsNone(s['judge']['mean_valid_only'])
        self.assertEqual(s['judge']['missing'],1)
        self.assertFalse(s['all_judgements_available'])

    def test_missing_and_valid_judge_denominators(self):
        class Mixed(Judge):
            def evaluate(self,r):
                self.score=None if len(self.inputs)==0 else 5
                return super().evaluate(r)
        a=case();b=case();b['eval_id']='synthetic_2'
        s=harness([a,b],System(record()),Mixed())['scorecard']
        self.assertEqual(s['judge']['valid'],1);self.assertEqual(s['judge']['missing'],1)
        self.assertEqual(s['judge']['mean_valid_only'],5)
        self.assertEqual(s['judge']['final_success_rate'],.5)

    def test_empty_duplicate_cases_fail_before_inference(self):
        for cases in [[],[case(),case()]]:
            with self.assertRaises(ValueError):validate_cases(cases)

    def test_invalid_output_never_gets_perfect_f1(self):
        r=record();r['output']['abstencion']='false'
        result=harness([case()],System(r),Judge())
        self.assertEqual(result['scorecard']['valid_output_rate'],0)
        self.assertEqual(result['scorecard']['reference_token_f1_mean'],0)


if __name__=='__main__':unittest.main()
