import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_rules_m3 import fact_present, implies_irregularity, score_case


class AuditRulesTests(unittest.TestCase):
    def test_numeric_boundaries(self):
        self.assertFalse(fact_present('168000000', '1680000000 COP'))
        self.assertFalse(fact_present('168000000', '1168000000 COP'))
        self.assertTrue(fact_present('168000000', '168.000.000 COP'))

    def test_empty_fact(self):
        self.assertFalse(fact_present('', 'anything'))

    def test_explicit_denial(self):
        self.assertFalse(fact_present('Mínima cuantía', 'No es mínima cuantía.'))
        self.assertTrue(fact_present('Mínima cuantía', 'Se registra mínima cuantía.'))

    def test_irregularity_insinuation_real_failure(self):
        self.assertTrue(implies_irregularity('Estas fechas no son cronológicamente consistentes, lo que sugiere una posible irregularidad.'))
        self.assertFalse(implies_irregularity('Esto no sugiere una posible irregularidad.'))
        self.assertFalse(implies_irregularity('No permite concluir irregularidad.'))

    def test_invalid_schema(self):
        row = score_case({'eval_id': 'x', 'kind': 'factual', 'required_facts': ['a']}, {'output': {}})
        self.assertFalse(row['valid_output'])
        self.assertFalse(row['domain_pass'])


if __name__ == '__main__':
    unittest.main()
