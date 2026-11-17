import json
from pathlib import Path
import tempfile
import unittest
from final.prepare_eval_final import build_common,build_calibration_review,canonical_hash,ROOT


class CommonEvalTests(unittest.TestCase):
    def test_common_has_same_approved_cases_and_no_answers_in_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'common'
            inputs,refs=build_common(folder)
            self.assertEqual(len(inputs),22)
            self.assertEqual({c['id'] for c in inputs},{r['id'] for r in refs})
            self.assertEqual(len({c['id'] for c in inputs}),22)
            for c in inputs:
                self.assertEqual(set(c),{'id','question','image','image_sha256'})
                if c['image']:self.assertTrue((ROOT/c['image']).is_file())
            dates=next(r for r in refs if r['id']=='m3_009')['required_facts']
            self.assertEqual(len(dates),2)
            self.assertTrue(next(r for r in refs if r['id']=='vis_06_missing_value')['expected_abstention'])
            self.assertFalse(next(r for r in refs if r['id']=='vis_04')['expected_abstention'])
            with self.assertRaises(FileExistsError):build_common(folder)

    def test_canonical_hash_ignores_json_whitespace(self):
        self.assertEqual(canonical_hash(json.loads('{"a": 1}')),canonical_hash(json.loads('{\n "a":1\n}')))

    def test_review_is_pending_not_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'calibration'
            build_calibration_review(folder)
            meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'],'human_review_pending')
            self.assertEqual(len(json.loads((folder/'anchors.json').read_text(encoding='utf-8'))),20)
