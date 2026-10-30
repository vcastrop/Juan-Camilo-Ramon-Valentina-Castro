import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from judge import IndependentJudge, evidence_payload, parse_judgement, summarize_judgements


class Generator:
    def __init__(self, outputs):
        self.outputs, self.inputs = iter(outputs), []
    def generate(self, system, user):
        self.inputs.append((system, json.loads(user)))
        value = next(self.outputs)
        if isinstance(value, Exception):
            raise value
        return value


class JudgeTests(unittest.TestCase):
    def record(self):
        return {'question': '¿Modalidad?', 'output': {'respuesta':'Directa', 'explicacion':'Figura en c1',
                'citas':['c1'], 'abstencion':False}, 'contexts':[{'chunk_id':'c1','text':'Modalidad: Directa'}],
                'correct':True, 'expected':'NO_LEAK', 'confidence':0.99, 'judge_score':5,
                'review_only':{'expected':'NO_LEAK'}, 'tool_trace':[]}

    def test_formats_and_bounds(self):
        for raw in ['{"puntaje":4,"razon":"Respaldada."}',
                    '```json\n{"puntaje":4,"razon":"Respaldada."}\n```',
                    'PUNTAJE=4,\nRAZÓN=Respaldada.']:
            self.assertEqual(parse_judgement(raw)['score'], 4)
        for raw in ['{"puntaje":true,"razon":"x"}', '{"puntaje":4.0,"razon":"x"}',
                    '{"puntaje":6,"razon":"x"}', '{"puntaje":0,"razon":"x"}',
                    '{"puntaje":4,"razon":""}', '{"puntaje":1,"puntaje":5,"razon":"x"}',
                    'PUNTAJE=3\nRAZON=x PUNTAJE=5', 'PUNTAJE=1\nPUNTAJE=5\nRAZON=x',
                    '{"puntaje":4,"razon":"x"} {"puntaje":5,"razon":"y"}']:
            with self.assertRaises(ValueError):
                parse_judgement(raw)

    def test_no_correctness_leak(self):
        payload = evidence_payload(self.record())
        self.assertNotIn('NO_LEAK', json.dumps(payload))
        self.assertNotIn('confidence', json.dumps(payload))
        self.assertNotIn('correct', json.dumps(payload))

    def test_score_never_overridden_by_correctness(self):
        generator = Generator(['{"puntaje":1,"razon":"La explicación no sustenta la conclusión."}'])
        result = IndependentJudge(generator).evaluate(self.record())
        self.assertEqual(result['score'], 1)
        self.assertEqual(len(result['attempts']), 1)
        self.assertFalse(result['score_adjusted'])

    def test_retry_only_format_and_preserve_attempts(self):
        gen = Generator(['bad', '{"puntaje":2,"razon":"Error relevante."}'])
        result = IndependentJudge(gen).evaluate(self.record())
        self.assertEqual(result['score'], 2)
        self.assertEqual(result['attempts'][0]['raw'], 'bad')
        self.assertIn('correccion_de_formato', gen.inputs[1][1])
        summary = summarize_judgements([result])
        self.assertEqual(summary['first_attempt_success_rate'], 0)
        self.assertEqual(summary['final_success_rate'], 1)

    def test_all_fail_missing_not_three_or_zero(self):
        result = IndependentJudge(Generator(['bad','bad'])).evaluate(self.record())
        self.assertIsNone(result['score'])
        summary = summarize_judgements([result])
        self.assertIsNone(summary['mean_valid_only'])
        self.assertEqual(summary['missing'], 1)
        self.assertEqual(summary['final_success_rate'], 0)
        self.assertIsNone(summarize_judgements([])['final_success_rate'])

    def test_generation_error_explicit(self):
        result = IndependentJudge(Generator([RuntimeError('model failed')])).evaluate(self.record())
        self.assertIsNone(result['score'])
        self.assertIsNotNone(result['attempts'][0]['generation_error'])

    def test_missing_explanation_not_fabricated(self):
        record = self.record()
        record['output']['explicacion'] = ''
        self.assertEqual(evidence_payload(record)['respuesta_propuesta']['explicacion'], '')

    def test_independent_tool_evidence(self):
        record = self.record()
        record['tool_trace'] = [{'tool_result':{'ok':True, 'operation':'abs(10 - 3) = 7 COP',
                                               'values_cop':{'a':'10','b':'3'}, 'expected':'NO_LEAK'}}]
        payload = evidence_payload(record)
        self.assertEqual(payload['calculos_verificables'][0]['operation'], 'abs(10 - 3) = 7 COP')
        self.assertNotIn('NO_LEAK', json.dumps(payload))

    def test_partial_denominator(self):
        good = IndependentJudge(Generator(['{"puntaje":4,"razon":"x"}'])).evaluate(self.record())
        bad = IndependentJudge(Generator(['bad','bad'])).evaluate(self.record())
        result = summarize_judgements([good,bad])
        self.assertEqual(result['final_success_rate'], .5)
        self.assertEqual(result['mean_valid_only'], 4)


if __name__ == '__main__':
    unittest.main()
