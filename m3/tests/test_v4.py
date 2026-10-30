import json
import sys
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_v4 import CompactAgent, normalize_decision
from contract_tools import ContractTools
from response_v4 import compact_contexts, generate_answer, CompactRAG
from test_agent import StubGenerator, StubRetriever, doc, ABSTAIN, CALL


class V4Tests(unittest.TestCase):
    def test_observed_alias_only(self):
        obj, change=normalize_decision('{"action":"diferencia_valores_contratos","arguments":{"id_a":"CO1.PCCNTR.1","id_b":"CO1.PCCNTR.2"}}')
        self.assertEqual(obj['action'],'tool')
        self.assertEqual(change,'tool_name_as_action')
        self.assertEqual(normalize_decision('{"action":"answer","result":"Ignored prose"}')[0],{'action':'answer'})
        for raw in ['I will call a tool', '{"action":"answer","name":"exec"}',
                    '{"action":"answer","action":"tool"}', '{"action":"exec","arguments":{}}']:
            with self.assertRaises(ValueError):
                normalize_decision(raw)

    def test_real_v3_trace_formats(self):
        root=Path(__file__).resolve().parents[1]
        with zipfile.ZipFile(root/'evidence/development_v3/contractrisk_m3_desarrollo_v3_resultados.zip') as z:
            rows=[json.loads(l) for l in z.read('predictions.jsonl').decode().splitlines()]
        row=next(r for r in rows if r['variant']=='agent_v3' and r['development_index']==4)
        decision,rule=normalize_decision(row['tool_trace'][0]['raw_response'])
        self.assertEqual(rule,'tool_name_as_action')
        self.assertEqual(decision['arguments']['id_a'],'CO1.PCCNTR.1180445')
        # A truncated final response must remain invalid, not be patched into an answer.
        gen=StubGenerator([row['raw_response'],row['raw_response']])
        result=generate_answer(gen,row['question'],row['contexts'])
        self.assertIsNone(result['output'])
        self.assertEqual(len(result['answer_attempts']),2)

    def test_compact_evidence_has_no_nested_metadata(self):
        contexts=[{'chunk_id':'c','doc_id':'d','text':'source','source_url':'url','start_char':0,'end_char':6}]
        self.assertEqual(set(compact_contexts(contexts)[0]),{'chunk_id','doc_id','text'})
        self.assertIn('source_url',contexts[0])

    def test_one_retry_format_not_semantic(self):
        gen=StubGenerator(['bad',ABSTAIN])
        record=generate_answer(gen,'question',[])
        self.assertFalse(record['first_attempt_valid'])
        self.assertTrue(record['output']['abstencion'])
        self.assertEqual(record['answer_attempts'][0]['raw_response'],'bad')
        self.assertIn('reparacion_formato',gen.inputs[1][1])
        valid_wrong=json.dumps({'respuesta':'wrong','explicacion':'wrong','citas':['c'],'abstencion':False})
        gen=StubGenerator([valid_wrong])
        record=generate_answer(gen,'question',[{'chunk_id':'c','doc_id':'d','text':'correct'}])
        self.assertEqual(len(record['answer_attempts']),1)
        self.assertEqual(record['output']['respuesta'],'wrong')

    def test_agent_stops_after_success_no_duplicate_tool_payload(self):
        tools=ContractTools([doc(1,'12'),doc(2,'2')])
        gen=StubGenerator([CALL,ABSTAIN])
        result=CompactAgent(StubRetriever(),gen,tools).predict('Diferencia de CO1.PCCNTR.1 y CO1.PCCNTR.2')
        self.assertEqual(result['termination'],'tool_success')
        self.assertEqual(result['tool_calls'],1)
        self.assertNotIn('contexts',gen.inputs[-1][1]['calculos'][0])
        self.assertEqual(gen.inputs[-1][1]['calculos'][0]['absolute_difference_cop'],'10')

    def test_no_tool_decision_stays_model_selected(self):
        gen=StubGenerator(['{"action":"answer"}',ABSTAIN])
        result=CompactAgent(StubRetriever(),gen,ContractTools([])).predict('¿Modalidad de CO1.PCCNTR.1?')
        self.assertEqual(result['termination'],'model_answer')
        self.assertEqual(result['tool_calls'],0)

    def test_control_same_protocol_empty_context(self):
        gen=StubGenerator(['bad',ABSTAIN])
        result=CompactRAG(StubRetriever(),gen).predict('question',retrieve=False)
        self.assertEqual(result['contexts'],[])
        self.assertEqual(len(result['answer_attempts']),2)

    def test_repeated_and_invalid_calls_stay_bounded(self):
        gen=StubGenerator([CALL,CALL,ABSTAIN])
        result=CompactAgent(StubRetriever(),gen,ContractTools([])).predict('CO1.PCCNTR.1 y CO1.PCCNTR.2')
        self.assertEqual(result['termination'],'duplicate_call')
        self.assertEqual(result['tool_calls'],1)
        gen=StubGenerator(['bad','bad','bad',ABSTAIN])
        result=CompactAgent(StubRetriever(),gen,ContractTools([])).predict('question')
        self.assertEqual(len(result['tool_trace']),3)
        self.assertEqual(result['termination'],'max_steps')


if __name__=='__main__':
    unittest.main()
