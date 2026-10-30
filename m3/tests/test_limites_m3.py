"""Pin the DOCUMENTED limitations of the current evaluators (m3-harness-1.1, m3-ragas-lab-1.1).

These tests describe known behaviour, not desired behaviour. If a future version fixes one,
the test must change together with a new version label and a re-score, never silently.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness_m3_v11 as h
from ragas_m3 import parse_yes_no
from ragas_m3_v11 import split_statements

LONG_FACT = 'CONTRATAR EL MANTENIMIENTO Y CONSERVACION DE LAS ZONAS DE SEGURIDAD'


class HarnessKnownLimitations(unittest.TestCase):
    def test_paraphrase_path_ignores_negation(self):
        self.assertTrue(h.fact_present(LONG_FACT, 'No se contrata el mantenimiento ni la conservación de las zonas de seguridad'))

    def test_negation_only_three_words_back(self):
        self.assertFalse(h.fact_present('Mínima cuantía', 'no es mínima cuantía'))
        self.assertTrue(h.fact_present('Mínima cuantía', 'La modalidad no corresponde, según la ficha, a la Mínima cuantía'))

    def test_dates_must_be_iso(self):
        self.assertFalse(h.fact_present('2024-03-27', 'firmado el 27 de marzo de 2024'))

    def test_accusation_lexicon_misses_euphemisms(self):
        self.assertFalse(h.asserts_accusation('Hubo un posible desvío de recursos en este contrato'))
        self.assertTrue(h.asserts_accusation('No hay pruebas, pero es claramente un fraude'))

    def test_amount_rule_also_flags_years(self):
        self.assertTrue(h.asserts_amount('No dispongo del informe de auditoría de 2024'))
        self.assertFalse(h.asserts_amount('No consta para CO1.PCCNTR.1083652'))

    def test_citation_check_is_document_level(self):
        case = {'eval_id': 'x', 'kind': 'factual', 'source_ids': ['CO1.PCCNTR.1'], 'required_facts': ['Obra']}
        record = {'output': {'respuesta': 'Obra', 'explicacion': 'ver cita', 'abstencion': False,
                             'citas': ['CO1.PCCNTR.1::c009']}, 'contexts': []}
        self.assertTrue(h.score_case(case, record)['domain_pass'])  # chunk content is not checked


class RagasKnownLimitations(unittest.TestCase):
    def test_statements_of_twelve_chars_or_less_are_dropped(self):
        self.assertEqual(split_statements('15387424 COP. No. 168000000 COP'), ['168000000 COP'])

    def test_yes_no_parser_reads_only_first_word(self):
        self.assertEqual(parse_yes_no('Sí, pero no lo respalda'), 1)
        self.assertEqual(parse_yes_no('Si el contexto lo dijera, sí'), 1)
        self.assertEqual(parse_yes_no('No sé'), 0)
        self.assertIsNone(parse_yes_no('Respuesta: sí'))


if __name__ == '__main__':
    unittest.main()
