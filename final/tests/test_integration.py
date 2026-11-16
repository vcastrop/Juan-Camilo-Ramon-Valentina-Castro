import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.integration import IntegratedSystem, parse_visual

DOC = {'doc_id': 'CO1.PCCNTR.123', 'text': 'Objeto registrado: Adquirir equipos', 'source_url': 'test-source'}


class IntegrationTests(unittest.TestCase):
    def visual(self, **updates):
        d = {'legible': True, 'texto_visible': 'CO1.PCCNTR.123', 'id_contrato': 'CO1.PCCNTR.123',
             'objeto': None, 'modalidad': None, 'valor_cop': None}
        d.update(updates)
        return json.dumps(d)

    def test_visual_schema(self):
        self.assertEqual(parse_visual(self.visual())['id_contrato'], DOC['doc_id'])

    def test_unreadable_cannot_assert(self):
        with self.assertRaises(ValueError):
            parse_visual(self.visual(legible=False))

    def test_absent_data_is_null(self):
        v = parse_visual(self.visual(legible=False, texto_visible=None, id_contrato=None))
        self.assertFalse(v['legible'])

    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):
            parse_visual(self.visual().replace('"legible": true', '"legible": true, "legible": false'))

    def test_id_requires_transcription(self):
        with self.assertRaises(ValueError):
            parse_visual(self.visual(texto_visible='nada'))

    def test_ambiguous_amount_rejected(self):
        with self.assertRaises(ValueError):
            parse_visual(self.visual(valor_cop='1.000.000'))

    def test_guard_does_not_call_generator(self):
        def forbidden(*args):
            self.fail('Generator called for missing source')
        s = IntegratedSystem([DOC], forbidden)
        for question in ['¿Qué concluyó la auditoría de CO1.PCCNTR.123?', 'Cláusula de multas de CO1.PCCNTR.123',
                         '¿Valor de CO1.PCCNTR.999?']:
            self.assertTrue(s.predict(question)['output']['abstencion'])

    def test_text_passes_only_inputs(self):
        seen = []
        def answer(q, visual):
            seen.append((q, visual))
            return {'output': {'respuesta': 'Dato', 'explicacion': 'Fuente', 'citas': ['x'], 'abstencion': False}, 'tool_calls': 1}
        r = IntegratedSystem([DOC], answer).predict('¿Objeto de CO1.PCCNTR.123?')
        self.assertEqual(seen, [('¿Objeto de CO1.PCCNTR.123?', None)])
        self.assertTrue(r['components']['tool'])

    def test_parse_failure_becomes_abstention(self):
        r = IntegratedSystem([DOC], lambda *args: {'output': None}).predict('¿Objeto de CO1.PCCNTR.123?')
        self.assertTrue(r['output']['abstencion'])

    def test_classifier_separate(self):
        class Classifier:
            def classify(self, text):
                return {'label': 'REQUIERE_REVISION', 'confidence': 0.6}
        r = IntegratedSystem([DOC], None, Classifier()).predict('Evaluar', mode='sufficiency', description='Servicios')
        self.assertTrue(r['components']['classifier'])
        self.assertFalse(r['components']['rag'])
        self.assertEqual(r['classification']['label'], 'REQUIERE_REVISION')

    def test_mismatching_image_id_abstains(self):
        output = parse_visual(self.visual())
        class Vision:
            def extract(self, image):
                return {'output': output, 'parse_error': None}
        r = IntegratedSystem([DOC], None, vision=Vision()).predict('¿Objeto de CO1.PCCNTR.456?', image=object())
        self.assertEqual(r['guard'], 'id_mismatch')

    def test_input_limits(self):
        s = IntegratedSystem([DOC], None)
        for q in ['', 'a'*1201]:
            with self.assertRaises(ValueError):
                s.predict(q)
        with self.assertRaises(ValueError):
            s.predict('Pregunta', mode='unknown')


if __name__ == '__main__':
    unittest.main()
