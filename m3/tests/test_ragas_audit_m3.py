import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ragas_audit_m3 import split_statements, parse_yes_no, aggregate, AuditedRagas


class RagasAuditTests(unittest.TestCase):
    def test_ids_amounts_and_sentences(self):
        text = 'CO1.PCCNTR.1109703::c003 indica 250.000.000 COP. La tasa es 2.5.'
        self.assertEqual(split_statements(text), ['CO1.PCCNTR.1109703::c003 indica 250.000.000 COP.', 'La tasa es 2.5.'])

    def test_short_claims_preserved(self):
        self.assertEqual(split_statements('Son 4 días. No hay multa.'), ['Son 4 días.', 'No hay multa.'])
        self.assertEqual(split_statements(''), [])

    def test_no_ambiguous_verdicts(self):
        self.assertEqual(parse_yes_no('Sí.'), 1)
        self.assertEqual(parse_yes_no('No'), 0)
        self.assertIsNone(parse_yes_no('Sí pero no'))

    def test_missing_not_dropped(self):
        self.assertIsNone(aggregate([1, None]))
        self.assertIsNone(aggregate([]))
        self.assertEqual(aggregate([1, 0]), .5)

    def test_partial_precision_is_missing(self):
        class Generator:
            def __init__(self):
                self.outputs = iter(['sí', 'tal vez'])
            def generate(self, system, user):
                return next(self.outputs)
        result = AuditedRagas(Generator(), None).context_precision(
            {'question': 'q', 'contexts': [{'text': 'a'}, {'text': 'b'}]}, 'r', [])
        self.assertIsNone(result['value'])
        self.assertEqual(result['relevance'], [1, None])


if __name__ == '__main__':
    unittest.main()
