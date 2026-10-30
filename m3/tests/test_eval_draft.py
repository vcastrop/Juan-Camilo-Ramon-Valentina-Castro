import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvalDraftTests(unittest.TestCase):
    def test_draft_is_not_claimed_as_approved(self):
        draft = json.loads((ROOT / 'eval/eval_set_draft.json').read_text(encoding='utf-8'))
        self.assertEqual(draft['status'], 'pending_human_review')
        self.assertTrue(all(c['review_status'] == 'pending' and not c['reviewer'] for c in draft['cases']))

    def test_sources_and_minimum_coverage(self):
        cases = json.loads((ROOT / 'eval/eval_set_draft.json').read_text(encoding='utf-8'))['cases']
        ids = {json.loads(line)['doc_id'] for line in (ROOT / 'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()}
        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(c['kind'] == 'unanswerable' for c in cases), 2)
        self.assertGreaterEqual(sum(c['kind'] == 'calculation' for c in cases), 2)
        self.assertEqual(len(cases), len({c['eval_id'] for c in cases}))
        for c in cases:
            self.assertTrue(c['input'] and c['expected'] and c['criterion'])
            self.assertTrue(set(c['source_ids']) <= ids)
        dev = json.loads((ROOT / 'eval/development_questions.json').read_text(encoding='utf-8'))['cases']
        self.assertFalse({c['input'] for c in cases} & {c['input'] for c in dev})


if __name__ == '__main__':
    unittest.main()
