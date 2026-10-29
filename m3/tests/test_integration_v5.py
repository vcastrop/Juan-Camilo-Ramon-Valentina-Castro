import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_v5 import CandidateAgent
from systems_v5 import CandidateRAG
from calibration_v1 import calibration_cases, verbose_equivalent, evaluate_calibration, summarize_calibration
from protocol_probe import ANSWER_V5, ROUTER_V5
from judge import evidence_payload
from contract_tools import ContractTools
from test_agent import StubGenerator, StubRetriever, ABSTAIN, CALL, doc


class IntegrationTests(unittest.TestCase):
    def test_response_prompt_identical_across_systems(self):
        gen=StubGenerator([ABSTAIN,'{"action":"answer"}',ABSTAIN])
        CandidateRAG(StubRetriever(),gen).predict('Question',retrieve=False)
        result=CandidateAgent(StubRetriever(),gen,ContractTools([])).predict('Question')
        self.assertEqual(gen.inputs[0][0],ANSWER_V5)
        self.assertEqual(gen.inputs[1][0],ROUTER_V5)
        self.assertEqual(gen.inputs[2][0],ANSWER_V5)
        self.assertEqual(gen.inputs[0][1],gen.inputs[2][1])
        self.assertEqual(result['tool_calls'],0)

    def test_candidate_tool_success_same_provenance(self):
        answer=json.dumps({'respuesta':'10 COP','explicacion':'12 - 2 = 10',
                           'citas':['CO1.PCCNTR.1::tool_value','CO1.PCCNTR.2::tool_value'],'abstencion':False})
        gen=StubGenerator([CALL,answer])
        result=CandidateAgent(StubRetriever(),gen,ContractTools([doc(1,'12'),doc(2,'2')])).predict('Diferencia CO1.PCCNTR.1 y CO1.PCCNTR.2')
        self.assertEqual(result['termination'],'tool_success')
        self.assertEqual(result['output']['respuesta'],'10 COP')
        self.assertEqual(result['tool_trace'][0]['tool_result']['absolute_difference_cop'],'10')
        self.assertEqual(len(result['contexts']),2)

    def test_twelve_equivalent_pairs_no_gold_or_score_payload(self):
        cases=calibration_cases()
        self.assertEqual(len(cases),12)
        self.assertEqual(len({c['id'] for c in cases}),12)
        self.assertEqual(sum(c['group']=='wrong' for c in cases),4)
        for case in cases:
            record=case['record']; original=copy.deepcopy(record)
            verbose=verbose_equivalent(record)
            self.assertEqual(record,original)
            self.assertEqual(verbose['contexts'],record['contexts'])
            for key in ['respuesta','explicacion']:
                self.assertEqual(verbose['output'][key],' '.join([record['output'][key]]*4).strip())
            for r in [record,verbose]:
                payload=evidence_payload(r)
                self.assertNotIn('expected_range_for_review',payload)
                self.assertNotIn('group',payload)

    def test_bias_counts_missing_pairs_not_zero(self):
        rows=[{'case_id':'a','condition':'before','length':'concise','expected_range_for_review':[4,5],
               'judgement':{'score':4,'attempts':[]}},
              {'case_id':'a','condition':'before','length':'verbose','expected_range_for_review':[4,5],
               'judgement':{'score':None,'attempts':[]}}]
        summary=summarize_calibration(rows)
        self.assertEqual(summary['before']['pairs_total'],1)
        self.assertEqual(summary['before']['pairs_valid'],0)
        self.assertIsNone(summary['before']['mean_absolute_difference'])
        self.assertEqual(summary['after']['judgements']['total'],0)

    def test_48_judgements_independent_and_never_adjusted(self):
        gen=StubGenerator(['{"puntaje":3,"razon":"Valor constante de prueba."}']*48)
        emitted=[]
        rows=evaluate_calibration(gen,emitted.append)
        self.assertEqual(len(rows),48)
        self.assertEqual(rows,emitted)
        self.assertTrue(all(r['judgement']['score']==3 for r in rows))
        for _,payload in gen.inputs:
            self.assertNotIn('expected_range_for_review',payload)
            self.assertNotIn('group',payload)
        summary=summarize_calibration(rows)
        self.assertEqual(summary['after']['pairs_valid'],12)
        self.assertEqual(summary['after']['mean_absolute_difference'],0)
        self.assertEqual(summary['after']['orientation_expected_range_matches'],0)

    def test_development_cases_unchanged(self):
        from run_integration_v5 import development_cases
        from run_agent_development import development_cases as old
        self.assertEqual(development_cases(),old())


if __name__=='__main__':
    unittest.main()
