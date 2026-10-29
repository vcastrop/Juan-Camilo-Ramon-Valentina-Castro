import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from protocol_probe import probe_cases,answer_v5,check_response,run_route,answer_schema
from test_agent import StubGenerator,ABSTAIN
from retrieval_advanced import ids_in


class ProbeTests(unittest.TestCase):
    def test_synthetic_separate_gold(self):
        cases,routes=probe_cases()
        self.assertEqual((len(cases),len(routes)),(6,4))
        root=Path(__file__).resolve().parents[1]
        gold=json.loads((root/'eval/gold_v1/eval_set.json').read_text(encoding='utf-8'))['cases']
        gold_ids=set().union(*(ids_in(c['input']) for c in gold))
        probe_ids=set().union(*(ids_in(c['question']) for c in cases+routes))
        self.assertFalse(gold_ids & probe_ids)

    def test_schema_no_placeholder_citation(self):
        cases,_=probe_cases()
        schema=answer_schema(cases[0]['contexts'])
        self.assertEqual(set(schema['required']),{'respuesta','explicacion','citas','abstencion'})
        self.assertNotIn('ID exacto del fragmento',json.dumps(schema))

    def test_repair_full_schema_previous_response_no_gold(self):
        cases,_=probe_cases()
        gen=StubGenerator(['{}',ABSTAIN])
        result=answer_v5(gen,cases[0])
        self.assertEqual(len(result['answer_attempts']),2)
        self.assertEqual(gen.inputs[1][1]['reparacion']['salida_anterior'],'{}')
        for _,payload in gen.inputs:
            self.assertNotIn('check',payload)
            self.assertNotIn('expected',payload)
            self.assertEqual(len(payload['esquema_salida']['required']),4)

    def test_wrong_number_not_marked_pass(self):
        cases,_=probe_cases()
        c=cases[-1]
        answer={'respuesta':'El resultado es 24150000 COP.','explicacion':'Explicación.',
                'citas':c['check']['citations'],'abstencion':False}
        self.assertFalse(check_response(c,answer)['mechanical_pass'])
        answer['respuesta']='El resultado es 241,500,000 COP.'
        self.assertTrue(check_response(c,answer)['mechanical_pass'])
        self.assertTrue(check_response(c,answer)['semantic_review_required'])

    def test_route_rejects_invented_id_even_valid_json(self):
        _,routes=probe_cases()
        r=routes[-1]
        gen=StubGenerator([json.dumps({'action':'tool','name':'diferencia_valores_contratos',
                                     'arguments':{'id_a':r['expected_ids'][0],'id_b':'CO1.PCCNTR.999'}})])
        result=run_route(gen,r,'v5')
        self.assertFalse(result['selection_correct'])
        self.assertEqual(len(result['attempts']),1)

    def test_absence_flag_not_semantic_proof(self):
        cases,_=probe_cases()
        answer=json.loads(ABSTAIN)
        answer['explicacion']='Fabricated claim here.'
        checks=check_response(cases[2],answer)
        self.assertTrue(checks['mechanical_pass'])
        self.assertTrue(checks['semantic_review_required'])


if __name__=='__main__':
    unittest.main()
