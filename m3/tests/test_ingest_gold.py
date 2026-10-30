import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest import chunk_documents


class IngestGoldTests(unittest.TestCase):
    def test_gold_integrity(self):
        folder = ROOT / 'eval/gold_v1'
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        for name, expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((folder / name).read_bytes()).hexdigest(), expected)
        gold = json.loads((folder / 'eval_set.json').read_text(encoding='utf-8'))
        self.assertEqual(len(gold['cases']), 12)
        self.assertTrue(all(c['review_status'].startswith('approved') for c in gold['cases']))
        self.assertIn('aparece truncado', gold['cases'][3]['expected'])
        self.assertNotIn('mínimas estipula', gold['cases'][3]['expected'])

    def test_chunks_preserve_source_and_cover_all_characters(self):
        docs = [json.loads(s) for s in (ROOT / 'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        for size in [400, 800]:
            chunks = chunk_documents(docs, size, 60)
            self.assertEqual(chunks, chunk_documents(docs, size, 60))
            for doc in docs:
                parts = [c for c in chunks if c['doc_id'] == doc['doc_id']]
                covered = set()
                for c in parts:
                    a, b = c['start_char'], c['end_char']
                    self.assertEqual(c['text'], doc['text'][a:b])
                    self.assertLessEqual(b-a, size)
                    covered.update(range(a, b))
                self.assertEqual(covered, set(range(len(doc['text']))))

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            chunk_documents([], 100, 100)


if __name__ == '__main__':
    unittest.main()
