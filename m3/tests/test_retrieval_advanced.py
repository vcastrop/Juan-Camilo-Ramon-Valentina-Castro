import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval_advanced import HybridRetriever, RerankedRetriever, ids_in, tokens, rrf
from rag_basic import parse_answer
from sqlite_support import check_fts5


class AdvancedTests(unittest.TestCase):
    def test_whole_identifiers_and_accents(self):
        self.assertEqual(ids_in('Ficha co1.pccntr.123?'), {'CO1.PCCNTR.123'})
        self.assertIn('co1.pccntr.123', tokens('Modalidad de CO1.PCCNTR.123'))
        self.assertIn('minima', tokens('Mínima cuantía'))

    def test_rrf_duplicate_not_double_counted(self):
        order, scores = rrf([['a','a'], ['b']])
        self.assertEqual(scores['a'], scores['b'])
        self.assertEqual(order, ['a','b'])

    def test_explicit_id_filter_and_unknown_id(self):
        chunks = [{'chunk_id':'a', 'doc_id':'CO1.PCCNTR.1','text':'Modalidad: prueba'},
                  {'chunk_id':'b', 'doc_id':'CO1.PCCNTR.2','text':'Otro contrato'}]
        class FakeDense:
            def search(self,q,k): return list(reversed(chunks))
        class FakeBM25:
            def __init__(self, rows): pass
            def get_scores(self, query): return [0,100]
        with patch.dict(sys.modules, {'rank_bm25':types.SimpleNamespace(BM25Okapi=FakeBM25)}):
            h = HybridRetriever(FakeDense(),chunks)
            self.assertEqual([c['chunk_id'] for c in h.search('CO1.PCCNTR.1',3)], ['a'])
            self.assertEqual(h.search('CO1.PCCNTR.999',3), [])

    def test_rerank_only_reorders_candidates(self):
        class Hybrid:
            def search(self,q,k): return [{'chunk_id':'a','doc_id':'X','text':'A'}, {'chunk_id':'b','doc_id':'Y','text':'B'}]
        class Scorer:
            def predict(self,pairs): return [0.1,0.9]
        self.assertEqual(RerankedRetriever(Hybrid(),Scorer()).search('Q',1)[0]['chunk_id'],'b')

    def test_abstention_true_empty_citations_valid(self):
        raw = '{"respuesta":"No consta","explicacion":"Faltan fuentes","citas":[],"abstencion":true}'
        self.assertTrue(parse_answer(raw,[])['abstencion'])

    def test_sqlite_capability_probe(self):
        class Connection:
            def __init__(self): self.closed = False
            def execute(self, sql): self.sql = sql
            def close(self): self.closed = True
        c = Connection()
        check_fts5(types.SimpleNamespace(connect=lambda name:c))
        self.assertIn('USING fts5',c.sql)
        self.assertTrue(c.closed)


if __name__ == '__main__':
    unittest.main()
