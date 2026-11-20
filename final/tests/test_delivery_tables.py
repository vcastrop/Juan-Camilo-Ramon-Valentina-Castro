import json
from pathlib import Path
import unittest

from final.build_delivery_tables import build, markdown


class DeliveryTablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        cls.result = build(cls.root)

    def test_preserved_tables_reproduce(self):
        folder = self.root / 'final/evidence/delivery_tables'
        self.assertEqual(self.result, json.loads((folder/'tables.json').read_text(encoding='utf-8')))
        self.assertEqual(markdown(self.result), (folder/'tables.md').read_text(encoding='utf-8'))

    def test_scope_and_limits_preserved(self):
        result = self.result
        self.assertEqual(len(result['rows']), 6)
        self.assertEqual(result['rows'][-1]['domain_pass'], 18)
        self.assertIsNone(result['rows'][-1]['peak_cuda_gib'])
        self.assertIn('no_efficiency_claim', result['rows'][-1]['timing_scope'])
        self.assertEqual(result['service_events'], {'accepted': 7, 'rejected': 3, 'total': 10, 'runtime_errors': 0})
        self.assertEqual(result['paid_calls_made_by_reproduction'], 0)
        self.assertFalse(result['new_inference_performed'])


if __name__ == '__main__':
    unittest.main()
