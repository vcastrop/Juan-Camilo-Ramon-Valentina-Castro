import json
from pathlib import Path
import tempfile
import unittest

from final.prepare_visual_review import prepare, fields_from_record


class VisualReviewTests(unittest.TestCase):
    def test_source_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            fields_from_record({'text': 'Identificador del contrato: a\nIdentificador del contrato: b'})

    def test_review_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'candidates'
            cases, refs = prepare(folder)
            self.assertEqual(len(cases), 10)
            self.assertEqual(len({c['id'] for c in cases}), 10)
            self.assertTrue(all(c['human_review'] == 'pending' for c in cases))
            by_id = {r['id']: r for r in refs}
            self.assertIsNone(by_id['vis_06_missing_value']['expected_visual_fields']['valor_cop'])
            self.assertTrue(by_id['vis_06_missing_value']['expected_abstention'])
            self.assertTrue(by_id['vis_08_blank']['expected_abstention'])
            for c in cases:
                self.assertFalse(Path(c['image']).is_absolute())
                self.assertTrue((folder/c['image']).is_file())
                if c['pair_with']:
                    self.assertEqual(by_id[c['id']]['expected_visual_fields'], by_id[c['pair_with']]['expected_visual_fields'])
            self.assertNotIn('expected_visual_fields', json.dumps(cases))
            with self.assertRaises(FileExistsError):
                prepare(folder)
