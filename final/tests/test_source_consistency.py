import copy
import json
from pathlib import Path
import unittest
import zipfile

from final.source_consistency import compare_visual_source
from final.integration import IntegratedSystem

ROOT=Path(__file__).resolve().parents[2]


class SourceConsistencyTests(unittest.TestCase):
    def setup_case(self, amount='100', modality='Mínima cuantía'):
        doc={'doc_id':'CO1.PCCNTR.123','source_url':'fixture',
             'text':f'Modalidad de contratación: {modality}\nValor del contrato (COP): {amount}'}
        visual={'legible':True,'texto_visible':'fixture','id_contrato':doc['doc_id'],
                'objeto':None,'valor_cop':'100','modalidad':'Mínima cuantía'}
        return doc,visual

    def test_decimal_equality_without_float(self):
        doc,visual=self.setup_case('100.00')
        self.assertEqual(compare_visual_source(visual,doc)['status'],'agreement_on_compared_fields')

    def test_factor_ten_conflict_not_prefix_match(self):
        doc,visual=self.setup_case('1000')
        report=compare_visual_source(visual,doc)
        self.assertEqual(report['status'],'conflict')
        self.assertEqual(report['conflicts'][0]['field'],'valor_cop')

    def test_no_ambiguous_source_value_selected(self):
        doc,visual=self.setup_case()
        doc['text']+='\nValor del contrato (COP): 999'
        report=compare_visual_source(visual,doc)
        self.assertIn('valor_cop',report['unverifiable_fields'])
        self.assertEqual(report['status'],'partial_agreement')

    def test_no_grouping_guess(self):
        doc,visual=self.setup_case('1.000.000')
        report=compare_visual_source(visual,doc)
        self.assertIn('valor_cop',report['unverifiable_fields'])

    def test_modality_normalizes_accents_not_meaning(self):
        doc,visual=self.setup_case(modality='MINIMA  CUANTIA')
        self.assertFalse(compare_visual_source(visual,doc)['conflicts'])
        visual['modalidad']='Contratación directa'
        self.assertEqual(compare_visual_source(visual,doc)['conflicts'][0]['field'],'modalidad')

    def test_unknown_or_mismatching_id_not_compared(self):
        doc,visual=self.setup_case()
        self.assertEqual(compare_visual_source(visual,None)['status'],'not_comparable')
        visual['id_contrato']='CO1.PCCNTR.999'
        self.assertEqual(compare_visual_source(visual,doc)['status'],'not_comparable')

    def test_visual_missing_not_filled(self):
        doc,visual=self.setup_case()
        visual['valor_cop']=None
        report=compare_visual_source(visual,doc)
        self.assertNotIn('valor_cop',report['compared_fields'])
        self.assertIsNone(visual['valor_cop'])

    def test_real_saved_failure_abstains_without_generator_or_mutation(self):
        with zipfile.ZipFile(ROOT/'final/evidence/visual_03/original_results.zip') as z:
            row=next(json.loads(s) for s in z.read('predictions.jsonl').decode().splitlines() if json.loads(s)['id']=='vis_04')
        docs=[json.loads(s) for s in (ROOT/'m3/corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        reading=row['result']['visual']
        original=copy.deepcopy(reading)
        class SavedVision:
            def extract(self,image): return reading
        def forbidden(*args): self.fail('Generator should not see contradictory evidence')
        system=IntegratedSystem(docs,forbidden,vision=SavedVision())
        result=system.predict('¿Qué modalidad y valor aparecen en la ficha de la imagen?',image=object())
        self.assertEqual(result['guard'],'visual_source_conflict')
        self.assertTrue(result['output']['abstencion'])
        self.assertEqual(result['output']['citas'],['IMAGE::input','CO1.PCCNTR.1088236::full_record'])
        self.assertIn('2500000000',result['output']['explicacion'])
        self.assertIn('250000000',result['output']['explicacion'])
        self.assertFalse(result['components']['rag'])
        self.assertEqual(reading,original)

    def test_agreement_continues_without_rewriting_reading(self):
        doc,visual=self.setup_case()
        class Vision:
            def extract(self,image): return {'output':visual,'parse_error':None}
        seen=[]
        def answer(q,context):
            seen.append(context)
            return {'output':{'respuesta':'100 COP','explicacion':'fixture','citas':['IMAGE::input'],'abstencion':False}}
        r=IntegratedSystem([doc],answer,vision=Vision()).predict('¿Valor de la imagen?',image=object())
        self.assertEqual(len(seen),1)
        self.assertIsNone(r['guard'])
        self.assertEqual(visual['valor_cop'],'100')

    def test_text_queries_unchanged(self):
        doc,_=self.setup_case()
        r=IntegratedSystem([doc],lambda *args:{'output':{'respuesta':'fixture','abstencion':False}}).predict('¿Valor?')
        self.assertNotIn('source_consistency',r)
