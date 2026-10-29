import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_m3
import harness_m3_v11 as v11
from ragas_m3 import split_statements as split_v10
from ragas_m3_v11 import LabRagasV11, METRICS, split_statements
from run_final_m3 import load_gold
from test_final_m3 import Encoder, YesNoGenerator, ctx, out

GOLD = {c['eval_id']: c for c in load_gold()}
RUN = Path(__file__).resolve().parents[1]/'results/final_m3'


class HarnessV11Tests(unittest.TestCase):
    def test_reported_false_positives_fixed(self):
        # Both were accepted by 1.0 (documented defect).
        self.assertTrue(harness_m3.fact_present('168000000', '1680000000 COP'))
        self.assertTrue(harness_m3.fact_present('Mínima cuantía', 'No es mínima cuantía'))
        self.assertFalse(v11.fact_present('168000000', '1680000000 COP'))
        self.assertFalse(v11.fact_present('Mínima cuantía', 'No es mínima cuantía'))
        self.assertTrue(v11.fact_present('168000000', '|250.000.000 - 82.000.000| = 168.000.000 COP'))
        self.assertTrue(v11.fact_present('Mínima cuantía', 'Modalidad: Mínima cuantía.'))
        self.assertTrue(v11.fact_present('2024-03-27', 'firma 2024-03-27T11:30:19.253'))

    def test_hedged_irregularity_is_flagged_negated_is_not(self):
        self.assertTrue(v11.asserts_accusation('Las fechas no son consistentes, lo que sugiere una posible irregularidad.'))
        self.assertFalse(v11.asserts_accusation(GOLD['m3_009']['expected']))
        self.assertFalse(v11.asserts_accusation('No permite concluir fraude ni sobrecosto.'))

    def test_gold_expected_answers_pass_v11(self):
        # Sanity: the reference answers themselves must not be penalised by the new rules.
        for case in GOLD.values():
            facts = v11.required_facts(case) if case['kind'] != 'unanswerable' else []
            for f in facts:
                self.assertTrue(v11.fact_present(f, case['expected']), (case['eval_id'], f))
            self.assertFalse(v11.asserts_accusation(case['expected']), case['eval_id'])

    def test_evidence_diagnostic_separates_document_from_field(self):
        record = dict(out('168000000 COP', ['CO1.PCCNTR.1088236::c000', 'CO1.PCCNTR.1109703::c000']),
                      contexts=[ctx('CO1.PCCNTR.1088236::c000', 'Entidad: AEROCIVIL'),
                                ctx('CO1.PCCNTR.1109703::c000', 'Entidad: AEROCIVIL')])
        row = v11.score_case(GOLD['m3_007'], record)
        self.assertEqual(row['evidence_retrieved'], 0.0)  # right documents, wrong fields
        record['contexts'] += [ctx('CO1.PCCNTR.1088236::tool_value', 'Valor del contrato (COP): 250000000'),
                               ctx('CO1.PCCNTR.1109703::tool_value', 'Valor del contrato (COP): 82000000')]
        record['tool_trace'] = [{'tool_result': {'ok': True, 'operation': 'abs(250000000 - 82000000) = 168000000 COP'}}]
        row = v11.score_case(GOLD['m3_007'], record)
        self.assertEqual(row['evidence_retrieved'], 0.0)
        self.assertEqual(row['evidence_with_tool'], 1.0)

    @unittest.skipUnless((RUN/'harness_rows.jsonl').exists(), 'saved run not present')
    def test_rescore_saved_run_never_changes_judge_or_answers(self):
        import rescore_m3
        with tempfile.TemporaryDirectory() as tmp:
            _, meta = rescore_m3.build(RUN, Path(tmp)/'out')
        self.assertFalse(meta['regenerated_answers'] or meta['regenerated_judgements'])
        self.assertEqual(sorted(meta['changed_vs_v1_0']), ['rag_avanzado/m3_009', 'sistema_final/m3_009'])
        items = [json.loads(l) for l in (RUN/'harness_rows.jsonl').read_text(encoding='utf-8').splitlines()]
        for item in items:
            row = v11.rescore(GOLD[item['row']['eval_id']], item)
            self.assertEqual(row['judge_score'], item['row']['judge_score'])


class RagasV11Tests(unittest.TestCase):
    def test_split_keeps_identifiers(self):
        text = 'La modalidad de CO1.PCCNTR.1109703 es Mínima cuantía. Se cita CO1.PCCNTR.1109703::c003 y 250.000.000 COP'
        self.assertIn('La modalidad de CO1', split_v10(text))  # 1.0 defect: ID split at its dots
        self.assertEqual(split_statements(text), ['La modalidad de CO1.PCCNTR.1109703 es Mínima cuantía',
                                                  'Se cita CO1.PCCNTR.1109703::c003 y 250.000.000 COP'])

    def test_lab_and_adapted_metrics_reported_with_na(self):
        record = {'question': GOLD['m3_010']['input'], 'variant': 'rag_avanzado',
                  'contexts': [ctx('CO1.PCCNTR.1109703::c003', 'Modalidad de contratación: Mínima cuantía'),
                               ctx('CO1.PCCNTR.1109703::c000', 'Departamento: Bogotá')],
                  'output': {'respuesta': 'Mínima cuantía registrada', 'explicacion': 'Según CO1.PCCNTR.1109703::c003.',
                             'citas': ['CO1.PCCNTR.1109703::c003'], 'abstencion': False}}
        r = LabRagasV11(YesNoGenerator(), Encoder()).evaluate(GOLD['m3_010'], record)
        self.assertEqual(r['faithfulness']['statements'], 2)
        self.assertEqual(r['context_precision_lab']['value'], 0.5)
        self.assertEqual(r['context_recall_lab']['value'], 1.0)
        self.assertAlmostEqual(r['context_precision_rank']['value'], 1.0)
        un = LabRagasV11(YesNoGenerator(), Encoder()).evaluate(GOLD['m3_012'], record)
        self.assertEqual({m for m in METRICS if un[m]['value'] is None}, set(METRICS) - {'faithfulness'})


if __name__ == '__main__':
    unittest.main()
