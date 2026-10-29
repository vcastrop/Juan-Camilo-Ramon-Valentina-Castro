import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ragas_course import CourseRagas,claims,summarize_ragas


class Generator:
    def __init__(self,outputs):self.outputs=iter(outputs)
    def generate(self,system,user):return next(self.outputs)


class RagasTests(unittest.TestCase):
    def test_claims_preserve_ids_and_decimals(self):
        self.assertEqual(len(claims('CO1.PCCNTR.123 cuesta 12.50. Otra frase.')),2)

    def test_strict_boolean_not_regex_yes_in_explanation(self):
        r=CourseRagas(Generator(['{"veredicto":false,"razon":"Sí hay un dato, pero no implica la afirmación"}']),None)
        self.assertEqual(r.binary_batch([{'x':1}])['value'],0)

    def test_partial_failures_do_not_disappear(self):
        r=CourseRagas(Generator(['{"veredicto":true,"razon":"x"}','invalid','invalid']),None)
        m=r.binary_batch([{'x':1},{'x':2}])
        self.assertIsNone(m['value']);self.assertEqual(m['status'],'error')
        self.assertEqual(len(m['details']),2)

    def test_empty_answer_not_perfect_faithfulness(self):
        r=CourseRagas(Generator([]),None).evaluate({'kind':'factual','input':'q','expected':'a'},{'output':None,'contexts':[]})
        self.assertIsNone(r['faithfulness']['value']);self.assertEqual(r['context_recall']['value'],0)

    def test_absent_document_na_and_coverage(self):
        r=CourseRagas(Generator([]),None).evaluate({'kind':'unanswerable','input':'q','expected':'a'},{'output':None,'contexts':[]})
        s=summarize_ragas([r]);self.assertEqual(s['context_recall']['not_applicable'],1)
        self.assertIsNone(s['context_recall']['mean_valid_only'])

    def test_cosine_and_bounded_reference_recall(self):
        g=Generator(['{"veredicto":true,"razon":"x"}']*3+['{"pregunta":"q"}'])
        r=CourseRagas(g,lambda texts:[[1,0],[1,0]]).evaluate(
            {'kind':'factual','input':'q','expected':'a'},
            {'output':{'respuesta':'a','explicacion':'','abstencion':False},
             'contexts':[{'chunk_id':'c','text':'a'}]})
        self.assertEqual(r['answer_relevancy']['value'],1)
        self.assertEqual(r['context_recall']['value'],1)


if __name__=='__main__':unittest.main()
