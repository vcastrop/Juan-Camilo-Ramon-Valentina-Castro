import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rag_basic import BasicRAG, parse_answer


class RagTests(unittest.TestCase):
    def test_unknown_citation_rejected(self):
        with self.assertRaises(ValueError):
            parse_answer(json.dumps(dict(respuesta='A', explicacion='B', citas=['inventada'], abstencion=False)), [])

    def test_abstention_requires_explanation(self):
        with self.assertRaises(ValueError):
            parse_answer(json.dumps(dict(respuesta='No consta', explicacion='', citas=[], abstencion=True)), [])

    def test_inference_interface_and_parse_failure_preserved(self):
        class Retriever:
            def search(self, q, k):
                return [{'chunk_id': 'test::0', 'text': 'Synthetic test source'}]
        class Generator:
            def generate(self, system, user):
                self.user = json.loads(user)
                return 'malformed output'
        gen = Generator()
        result = BasicRAG(Retriever(), gen).predict('Test question')
        self.assertEqual(set(gen.user), {'pregunta', 'fragmentos'})
        self.assertEqual(result['raw_response'], 'malformed output')
        self.assertIsNone(result['output'])
        self.assertTrue(result['parse_error'])


if __name__ == '__main__':
    unittest.main()
