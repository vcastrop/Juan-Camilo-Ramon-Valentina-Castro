import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contract_tools import ContractTools, TOOL_NAME
from rag_agent import AgentRAG, parse_decision, SYSTEM_V3
from structured_output import parse_object


def doc(number, amount):
    return {'doc_id': 'CO1.PCCNTR.'+str(number), 'source_url': 'https://example.org/source',
            'text': 'Entidad: Ejemplo\nValor del contrato (COP): '+str(amount)}


class StubRetriever:
    def search(self, question, k):
        return []


class StubGenerator:
    def __init__(self, outputs):
        self.outputs, self.inputs = iter(outputs), []
    def generate(self, system, user):
        self.inputs.append((system, json.loads(user)))
        return next(self.outputs)


ABSTAIN = json.dumps({'respuesta': 'No consta en las fuentes.', 'explicacion': 'Falta evidencia.',
                      'citas': [], 'abstencion': True})
CALL = json.dumps({'action': 'tool', 'name': TOOL_NAME,
                   'arguments': {'id_a': 'CO1.PCCNTR.1', 'id_b': 'CO1.PCCNTR.2'}})


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.documents = [doc(1, '12.25'), doc(2, '2.10')]
        self.tools = ContractTools(self.documents)
        self.args = {'id_a': 'CO1.PCCNTR.1', 'id_b': 'CO1.PCCNTR.2'}
        self.ids = set(self.args.values())

    def test_exact_decimal_and_source_offsets(self):
        result = self.tools.execute(TOOL_NAME, self.args, self.ids)
        self.assertTrue(result['ok'])
        self.assertEqual(result['absolute_difference_cop'], '10.15')
        for c, d in zip(result['contexts'], self.documents):
            self.assertEqual(c['text'], d['text'][c['start_char']:c['end_char']])

    def test_large_decimal_does_not_round(self):
        t = ContractTools([doc(1, '12345678901234567890123456789.12'), doc(2, '0.01')])
        self.assertEqual(t.execute(TOOL_NAME, self.args, self.ids)['absolute_difference_cop'],
                         '12345678901234567890123456789.11')

    def test_rejects_unknown_tool_ids_extra_args(self):
        self.assertFalse(self.tools.execute('exec', self.args, self.ids)['ok'])
        self.assertFalse(self.tools.execute(TOOL_NAME, dict(self.args, path='/tmp'), self.ids)['ok'])
        self.assertFalse(self.tools.execute(TOOL_NAME, self.args, {'CO1.PCCNTR.1'})['ok'])
        missing = {'id_a': 'CO1.PCCNTR.1', 'id_b': 'CO1.PCCNTR.999'}
        self.assertFalse(self.tools.execute(TOOL_NAME, missing, set(missing.values()))['ok'])

    def test_missing_ambiguous_amount_no_fallback(self):
        for value in ['1,000', 'No disponible', '-1', '12\nValor del contrato (COP): 13']:
            t = ContractTools([doc(1, value), doc(2, '2')])
            self.assertFalse(t.execute(TOOL_NAME, self.args, self.ids)['ok'])

    def test_timeout_records_failure(self):
        with patch('contract_tools.time.perf_counter', side_effect=[0, 3, 4]):
            result = self.tools.execute(TOOL_NAME, self.args, self.ids)
        self.assertFalse(result['ok'])
        self.assertIn('budget', result['error'])

    def test_fence_allowed_but_ambiguity_rejected(self):
        self.assertEqual(parse_decision('```json\n{"action":"answer"}\n```'), {'action':'answer'})
        for raw in ['{"action":"answer","action":"tool"}', '{} {}', '[]',
                    '{"action":"answer","extra":1}', '{"action":NaN}']:
            with self.assertRaises(ValueError):
                parse_decision(raw)
        with self.assertRaises(ValueError):
            parse_object('{"a":{"b":1,"b":2}}')

    def test_agent_real_function_stub_model_trace(self):
        answer = json.dumps({'respuesta':'La diferencia es 10.15 COP.',
                             'explicacion':'abs(12.25 - 2.10) = 10.15 COP.',
                             'citas':['CO1.PCCNTR.1::tool_value','CO1.PCCNTR.2::tool_value'],
                             'abstencion':False})
        generator = StubGenerator([CALL, '{"action":"answer"}', answer])
        result = AgentRAG(StubRetriever(), generator, self.tools).predict(
            'Diferencia de CO1.PCCNTR.1 y CO1.PCCNTR.2')
        self.assertEqual(result['tool_calls'], 1)
        self.assertEqual(result['termination'], 'model_answer')
        self.assertIsNotNone(result['output'])
        self.assertEqual(generator.inputs[-1][0], SYSTEM_V3)
        self.assertEqual(len(result['contexts']), 2)
        self.assertNotIn('expected', json.dumps(generator.inputs))

    def test_model_can_choose_no_tool(self):
        gen = StubGenerator(['{"action":"answer"}', ABSTAIN])
        result = AgentRAG(StubRetriever(), gen, self.tools).predict('¿Qué contiene el informe ausente?')
        self.assertEqual(result['tool_calls'], 0)
        self.assertTrue(result['output']['abstencion'])

    def test_bad_decisions_bounded_and_preserved(self):
        gen = StubGenerator(['invalid', 'invalid', 'invalid', ABSTAIN])
        result = AgentRAG(StubRetriever(), gen, self.tools).predict('Pregunta')
        self.assertEqual(result['termination'], 'max_steps')
        self.assertEqual(len(result['tool_trace']), 3)
        self.assertTrue(all(e['parse_error'] for e in result['tool_trace']))

    def test_repeated_call_blocked(self):
        gen = StubGenerator([CALL, CALL, ABSTAIN])
        result = AgentRAG(StubRetriever(), gen, self.tools).predict('CO1.PCCNTR.1 y CO1.PCCNTR.2')
        self.assertEqual(result['termination'], 'duplicate_call')
        self.assertEqual(result['tool_calls'], 1)

    def test_tool_error_does_not_create_evidence(self):
        gen = StubGenerator([CALL, '{"action":"answer"}', ABSTAIN])
        result = AgentRAG(StubRetriever(), gen, self.tools).predict('CO1.PCCNTR.1')
        self.assertEqual(result['contexts'], [])
        self.assertFalse(result['tool_trace'][0]['tool_result']['ok'])

    def test_invalid_final_answer_not_repaired_to_success(self):
        gen = StubGenerator(['{"action":"answer"}', '{"respuesta":"Inventada"}'])
        result = AgentRAG(StubRetriever(), gen, self.tools).predict('Pregunta')
        self.assertIsNone(result['output'])
        self.assertTrue(result['parse_error'])

    def test_steps_configuration(self):
        for n in [0, 4, True]:
            with self.assertRaises(ValueError):
                AgentRAG(StubRetriever(), None, self.tools, max_steps=n)

    def test_development_cases_separate_from_gold(self):
        from run_agent_development import development_cases
        root = Path(__file__).resolve().parents[1]
        gold = json.loads((root/'eval/gold_v1/eval_set.json').read_text(encoding='utf-8'))['cases']
        from retrieval_advanced import ids_in
        gold_ids = set().union(*(ids_in(c['input']) for c in gold))
        cases = development_cases()
        self.assertEqual(len(cases), 8)
        self.assertEqual(sum(c['tool_expected_for_review'] for c in cases), 2)
        self.assertFalse(set().union(*(ids_in(c['input']) for c in cases)) & gold_ids)


if __name__ == '__main__':
    unittest.main()
