from pathlib import Path
import tempfile
import unittest
from final.replay_source_guard import run


class SourceReplayTests(unittest.TestCase):
    def test_saved_corpus_and_responses_replay_without_gpu(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'replay'
            meta=run(output)
            self.assertEqual(meta['blocked_ids'],['vis_04'])
            self.assertEqual(meta['output_changed_ids'],['vis_04'])
            self.assertEqual(meta['case_count'],10)
            self.assertFalse(meta['model_inference_performed'])
            with self.assertRaises(FileExistsError): run(output)
