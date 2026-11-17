import json
import unittest

from final.judge_final import FinalJudge
from final.calibration_final import cases,verbose,schedule,summarize
from final.generators import precision_settings


class FakeGenerator:
    def __init__(self,outputs):self.outputs=iter(outputs);self.calls=[]
    def generate(self,system,user):
        self.calls.append((system,json.loads(user)))
        return next(self.outputs)


class FinalJudgeTests(unittest.TestCase):
    def test_synthetic_cases_and_schedule(self):
        items=cases()
        self.assertEqual(len(items),20)
        self.assertEqual(len({c['id'] for c in items}),20)
        self.assertEqual(len(schedule()),38)
        self.assertNotIn('CO1.PCCNTR',json.dumps(items))
        self.assertEqual(sum(c['group']=='bad' for c in items),10)

    def test_expected_range_and_correctness_flags_never_enter_judge(self):
        item=cases()[0];record=dict(item['record'],expected='forbidden',correct=True,expected_score_range=[4,5],judge_score=5)
        gen=FakeGenerator(['{"puntaje":1,"razon":"Prueba"}'])
        result=FinalJudge(gen).evaluate(record)
        self.assertEqual(result['score'],1)
        self.assertEqual(len(gen.calls),1)
        self.assertFalse(result['score_adjusted'])
        for key in ['expected','correct','expected_score_range','judge_score']:
            self.assertNotIn(key,gen.calls[0][1])

    def test_only_invalid_format_retried(self):
        gen=FakeGenerator(['not json','{"puntaje":2,"razon":"Error concreto"}'])
        result=FinalJudge(gen).evaluate(cases()[0]['record'])
        self.assertEqual(result['score'],2)
        self.assertEqual(len(result['attempts']),2)
        self.assertEqual(result['attempts'][0]['raw'],'not json')

    def test_two_invalid_responses_stay_missing(self):
        gen=FakeGenerator(['{"puntaje":true,"razon":"x"}','{"puntaje":5,"puntaje":1,"razon":"x"}'])
        result=FinalJudge(gen).evaluate(cases()[0]['record'])
        self.assertIsNone(result['score'])
        self.assertEqual(len(gen.calls),2)

    def synthetic_rows(self):
        by_id={c['id']:c for c in cases()}
        return [{'condition':condition,'id':cid,'judgement':{'score':5 if by_id[cid]['group']=='good' else 1}}
                for condition,cid in schedule()]

    def test_ideal_synthetic_scores_pass_gate_not_human_audit(self):
        result=summarize(self.synthetic_rows())
        self.assertTrue(result['gate_passed'])
        self.assertTrue(result['human_semantic_audit_required'])

    def test_one_bad_accepted_blocks_gate(self):
        rows=self.synthetic_rows()
        next(r for r in rows if r['id']=='number_bad' and r['condition']=='main_mitigated')['judgement']['score']=4
        self.assertFalse(summarize(rows)['gate_passed'])

    def test_missing_duplicate_and_verbosity_regressions_fail(self):
        rows=self.synthetic_rows();rows[-1]=rows[-2]
        self.assertFalse(summarize(rows)['gate_passed'])
        rows=self.synthetic_rows()
        next(r for r in rows if r['id']=='short_bad' and r['condition']=='after_verbose')['judgement']['score']=5
        self.assertFalse(summarize(rows)['gate_passed'])

    def test_verbose_only_repeats_claims_and_does_not_mutate(self):
        record=cases()[0]['record'];original=json.dumps(record,sort_keys=True)
        changed=verbose(record)
        self.assertEqual(changed['output']['respuesta'],' '.join([record['output']['respuesta']]*4))
        self.assertEqual(json.dumps(record,sort_keys=True),original)

    def test_precision_plan_no_bfloat16_or_silent_fallback(self):
        self.assertEqual(precision_settings('nf4')['compute_dtype'],'float16')
        self.assertTrue(precision_settings('nf4')['double_quantization'])
        with self.assertRaises(ValueError):precision_settings('auto')
