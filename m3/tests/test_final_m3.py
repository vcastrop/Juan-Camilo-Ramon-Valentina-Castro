import csv
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness_m3
from harness_m3 import fact_present, harness, required_facts, score_case, scorecard
from ragas_m3 import LabRagas, YES_NO_SYSTEM, parse_yes_no, split_statements, summarize
from protocol_probe import ANSWER_V5, ROUTER_V5
from run_final_m3 import load_gold

GOLD = {c['eval_id']: c for c in load_gold()}


def out(respuesta, citas=(), abstencion=False, explicacion='Según la ficha citada.'):
    return {'output': {'respuesta': respuesta, 'explicacion': explicacion, 'citas': list(citas),
                       'abstencion': abstencion}, 'contexts': [], 'latency_seconds': 1.0}


class HarnessRuleTests(unittest.TestCase):
    def test_gold_frozen_with_two_unanswerable(self):
        self.assertEqual(len(GOLD), 12)
        self.assertEqual(sum(c['kind'] == 'unanswerable' for c in GOLD.values()), 2)
        self.assertEqual(required_facts(GOLD['m3_009']), ['2019-09-10', '2024-03-27'])

    def test_calculation_with_thousand_separators_and_both_sources(self):
        r = score_case(GOLD['m3_007'], out('|250.000.000 - 82.000.000| = 168.000.000 COP',
                                           ['CO1.PCCNTR.1088236::tool_value', 'CO1.PCCNTR.1109703::c005']))
        self.assertEqual(r['accuracy'], 1.0)
        self.assertTrue(r['domain_pass'])

    def test_wrong_number_and_missing_citation(self):
        r = score_case(GOLD['m3_007'], out('168000001', ['CO1.PCCNTR.1088236::c005'],
                                           explicacion='250000000 y 82000000'))
        self.assertAlmostEqual(r['accuracy'], 2/3)
        self.assertIn('falta_cita_requerida', r['domain_reasons'])
        self.assertFalse(r['domain_pass'])

    def test_foreign_contract_citation_fails_domain(self):
        r = score_case(GOLD['m3_010'], out('Mínima cuantía', ['CO1.PCCNTR.1109703::c003', 'CO1.PCCNTR.5193000::c005']))
        self.assertEqual(r['accuracy'], 1.0)
        self.assertEqual(r['domain_reasons'], ['cita_ficha_ajena'])

    def test_paraphrase_tolerance_m3_004_but_numbers_exact(self):
        text = ('INSTITUTO DE FINANCIAMIENTO; PROMOCION Y DESARROLLO DE CALDAS contrata intermediación de seguros '
                'para asesorar a Infi-Caldas en la contratación y administración del programa de seguros')
        r = score_case(GOLD['m3_004'], out(text, ['CO1.PCCNTR.3577214::c001']))
        self.assertEqual(r['accuracy'], 1.0)
        self.assertFalse(fact_present('168000000', '16800000 COP'))
        self.assertFalse(fact_present('Mínima cuantía', 'Contratación directa'))

    def test_abstention_on_answerable_scores_zero(self):
        r = score_case(GOLD['m3_010'], out('No dispongo del dato', [], True, 'Mínima cuantía no aparece'))
        self.assertEqual(r['accuracy'], 0.0)
        self.assertIn('abstencion_indebida', r['domain_reasons'])

    def test_unanswerable_abstention_and_amount_contradiction(self):
        good = score_case(GOLD['m3_011'], out('No dispongo del texto de la cláusula de CO1.PCCNTR.1088236.', [], True))
        self.assertEqual((good['accuracy'], good['domain_pass']), (1.0, True))
        # v5 failure: abstencion=true while asserting figures.
        bad = score_case(GOLD['m3_011'], out('La multa es de 2900000 COP', [], True))
        self.assertEqual(bad['accuracy'], 1.0)
        self.assertEqual(bad['domain_reasons'], ['afirma_cifras'])
        invent = score_case(GOLD['m3_012'], out('La auditoría concluyó que fue aprobado', ['CO1.PCCNTR.1083652::c002']))
        self.assertEqual((invent['accuracy'], invent['domain_pass']), (0.0, False))

    def test_accusation_unless_negated(self):
        ok = score_case(GOLD['m3_009'], out('Firma 2024-03-27 e inicio 2019-09-10; no permite concluir fraude.',
                                            ['CO1.PCCNTR.1088236::c002']))
        self.assertTrue(ok['domain_pass'])
        bad = score_case(GOLD['m3_009'], out('Firma 2024-03-27 e inicio 2019-09-10: hubo fraude.',
                                             ['CO1.PCCNTR.1088236::c002']))
        self.assertIn('acusacion', bad['domain_reasons'])

    def test_invalid_output(self):
        r = score_case(GOLD['m3_001'], {'output': None})
        self.assertEqual((r['accuracy'], r['domain_pass'], r['domain_reasons']), (0.0, False, ['salida_invalida']))


class StubJudge:
    def __init__(self, scores):
        self.scores, self.seen = iter(scores), []
    def evaluate(self, record):
        self.seen.append(record)
        s = next(self.scores)
        return {'score': s, 'reason': None if s is None else 'r', 'attempts': []}


class HarnessRunTests(unittest.TestCase):
    def test_system_receives_only_question_and_failures_are_counted(self):
        cases = [GOLD['m3_010'], GOLD['m3_011'], GOLD['m3_001']]
        received = []
        def sistema(q):
            received.append(q)
            if q == cases[2]['input']:
                raise RuntimeError('boom')
            if q == cases[0]['input']:
                return dict(out('Mínima cuantía', ['CO1.PCCNTR.1109703::c003']), latency_seconds=2.0)
            return dict(out('No consta.', [], True), latency_seconds=4.0)
        rows, card = harness(cases, sistema, StubJudge([5, None, 1]), None, None, 'x')
        self.assertEqual(received, [c['input'] for c in cases])
        self.assertTrue(all(isinstance(q, str) for q in received))
        self.assertEqual(card['system_errors'], 1)
        self.assertEqual(card['dim2_judge_valid'], 2)
        self.assertEqual(card['dim2_judge_mean'], 3)
        self.assertEqual(card['dim3_domain_passed'], 2)
        self.assertEqual(card['latency_median_seconds'], 3.0)
        self.assertEqual(card['latency_cases'], 2)
        self.assertAlmostEqual(card['dim1_accuracy'], 2/3)
        self.assertEqual(card['m2_compatible_rate'], 1/3)
        self.assertEqual(rows[2]['row']['system_error'], 'RuntimeError: boom')

    def test_scorecard_all_missing_judges(self):
        rows = [dict(score_case(GOLD['m3_011'], out('No consta', [], True)), judge_score=None,
                     m2_compatible_pass=False, latency_seconds=None)]
        card = scorecard(rows)
        self.assertIsNone(card['dim2_judge_mean'])
        self.assertIsNone(card['latency_median_seconds'])


class YesNoGenerator:
    """Answers 'Sí' unless the quoted claim/passage contains `no_if`; question generation is fixed."""
    def __init__(self, no_if='Bogotá', garbage_if=None):
        self.no_if, self.garbage_if, self.calls = no_if, garbage_if, []
    def generate(self, system, user):
        self.calls.append((system, user))
        if system != YES_NO_SYSTEM:
            return '¿Qué modalidad registra la ficha?'
        quoted = user.rsplit('"', 2)[-2]
        if self.garbage_if and self.garbage_if in quoted:
            return 'Tal vez'
        return 'No.' if self.no_if in quoted else 'Sí, lo respalda.'


class Encoder:
    def encode(self, texts):
        import numpy as np
        return [np.array([1.0, float('modalidad' in t.lower())]) for t in texts]


def ctx(cid, text):
    return {'chunk_id': cid, 'doc_id': cid.split('::')[0], 'text': text}


class RagasTests(unittest.TestCase):
    def test_strict_yes_no(self):
        self.assertEqual([parse_yes_no(x) for x in ['Sí.', 'si', 'No, falta', 'Yes', 'Tal vez sí', '', None]],
                         [1, 1, 0, 1, None, None, None])

    def test_split_keeps_numbers(self):
        self.assertEqual(split_statements('Valor 250.000.000 COP. Diferencia de 168.000.000 calculada'),
                         ['Valor 250.000.000 COP', 'Diferencia de 168.000.000 calculada'])

    def test_metrics_and_na(self):
        record = {'question': GOLD['m3_010']['input'], 'variant': 'rag_ingenuo',
                  'contexts': [ctx('CO1.PCCNTR.1109703::c003', 'Modalidad de contratación: Mínima cuantía'),
                               ctx('CO1.PCCNTR.1109703::c000', 'Departamento: Bogotá'),
                               ctx('CO1.PCCNTR.1109703::c004', 'Modalidad otra vez Mínima cuantía')],
                  'output': {'respuesta': 'Mínima cuantía registrada', 'explicacion': 'Campo Modalidad en Bogotá citado',
                             'citas': ['CO1.PCCNTR.1109703::c003'], 'abstencion': False}}
        r = LabRagas(YesNoGenerator(), Encoder()).evaluate(GOLD['m3_010'], record)
        self.assertEqual(r['faithfulness']['statements'], 2)
        self.assertEqual(r['faithfulness']['value'], 0.5)  # second claim contains Bogotá -> 'No'
        self.assertAlmostEqual(r['context_precision']['value'], (1 + 2/3)/2)
        self.assertAlmostEqual(r['context_precision']['simple_fraction'], 2/3)
        self.assertEqual(r['context_recall']['value'], 1.0)
        self.assertIsNotNone(r['answer_relevancy']['value'])
        self.assertTrue(r['source_hit'])
        un = LabRagas(YesNoGenerator(), Encoder()).evaluate(
            GOLD['m3_011'], dict(record, output={'respuesta': 'No consta', 'explicacion': 'Falta', 'citas': [], 'abstencion': True}))
        for m in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
            self.assertIsNone(un[m]['value'])
        self.assertEqual(un['judge_calls'], [])
        self.assertIsNone(un['source_hit'])

    def test_parse_failures_excluded_and_counted(self):
        record = {'question': 'q', 'variant': 'v', 'contexts': [ctx('CO1.PCCNTR.1109703::c003', 'dudoso')],
                  'output': {'respuesta': 'Mínima cuantía registrada', 'explicacion': 'x', 'citas': [], 'abstencion': False}}
        r = LabRagas(YesNoGenerator(garbage_if='dudoso'), Encoder()).evaluate(GOLD['m3_010'], record)
        self.assertIsNone(r['context_precision']['value'])
        self.assertGreater(r['judge_parse_failures'], 0)
        s = summarize([r])
        self.assertEqual(s['context_precision_n'], 0)
        self.assertEqual(s['context_precision_na'], 0)

    def test_tool_operation_is_part_of_context(self):
        record = {'question': GOLD['m3_007']['input'], 'variant': 'sistema_final', 'contexts': [],
                  'tool_trace': [{'tool_result': {'ok': True, 'operation': 'abs(250000000 - 82000000) = 168000000 COP'}}],
                  'output': {'respuesta': 'La diferencia es 168000000 COP', 'explicacion': 'x', 'citas': [], 'abstencion': False}}
        gen = YesNoGenerator()
        LabRagas(gen, Encoder()).evaluate(GOLD['m3_007'], record)
        self.assertIn('[calculo] abs(250000000 - 82000000)', gen.calls[0][1])


class StubDense:
    def __init__(self, chunks):
        self.chunks = chunks
        self.encoder = Encoder()
    def search(self, q, k):
        return [dict(c) for c in self.chunks[:k]]


class ScriptedGenerator:
    def __init__(self):
        self.systems = []
    def generate(self, system, user):
        self.systems.append(system)
        if system == ROUTER_V5:
            return '{"action":"answer"}'
        return json.dumps({'respuesta': 'No consta', 'explicacion': 'Falta evidencia', 'citas': [], 'abstencion': True})


class SystemsAndReportTests(unittest.TestCase):
    def test_variants_share_prompt_and_report_recomputes(self):
        class FakeBM25:
            def __init__(self, rows): self.n = len(rows)
            def get_scores(self, query): return [0]*self.n
        class Scorer:
            def predict(self, pairs): return [0.0]*len(pairs)
        chunks = [ctx('CO1.PCCNTR.1109703::c000', 'Modalidad de contratación: Mínima cuantía'),
                  ctx('CO1.PCCNTR.1088236::c000', 'Valor del contrato (COP): 250000000')]
        docs = [{'doc_id': 'CO1.PCCNTR.1109703', 'text': 'x', 'source_url': 'u'}]
        gen = ScriptedGenerator()
        with patch.dict(sys.modules, {'rank_bm25': types.SimpleNamespace(BM25Okapi=FakeBM25)}):
            import sistemas_m3
            systems = sistemas_m3.construir(StubDense(chunks), chunks, Scorer(), gen, docs)
        self.assertEqual(set(systems), set(sistemas_m3.MAIN + sistemas_m3.ABLATIONS))
        cases = [GOLD['m3_010'], GOLD['m3_011']]
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            with (results/'harness_rows.jsonl').open('w', encoding='utf-8') as f:
                for name, system in systems.items():
                    rows, _ = harness(cases, system, StubJudge([4, 5]), Encoder(), None, name)
                    for r in rows:
                        self.assertEqual(r['record']['variant'], name)
                        f.write(json.dumps(r, ensure_ascii=False)+'\n')
                    if name == 'sin_rag':
                        self.assertTrue(all(r['record']['contexts'] == [] for r in rows))
            import report_m3
            table = report_m3.build(results)
            with (results/'scorecard_m3.csv').open(encoding='utf-8') as f:
                card = list(csv.DictReader(f))
            self.assertEqual([c['variant'] for c in card], sistemas_m3.MAIN + sistemas_m3.ABLATIONS)
            self.assertEqual(card[0]['dim3_domain_passed'], '1')  # abstains on both: only m3_011 passes
            self.assertIn('Sistema final', table)
        self.assertEqual({s for s in gen.systems}, {ANSWER_V5, ROUTER_V5})


if __name__ == '__main__':
    unittest.main()
