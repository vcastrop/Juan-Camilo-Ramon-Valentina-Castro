import json
from pathlib import Path
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.visual_fields import transcription_to_visual, amount_literal, requested_missing
from final.tool_policy import eligible_difference


class CorrectionTests(unittest.TestCase):
    def transcribe(self, text):
        return transcription_to_visual(json.dumps({'legible': True, 'texto_visible': text}))[0]

    def test_saved_real_readable_transcriptions(self):
        with zipfile.ZipFile(ROOT/'final/evidence/integration_01/original_results.zip') as z:
            rows = [json.loads(x) for x in z.read('integration_rows.jsonl').decode().splitlines()]
        readable = [r for r in rows if r['stage']=='visual_component' and r['case_id']!='visual_blank']
        self.assertEqual(len(readable), 3)
        for row in readable:
            parsed, evidence = transcription_to_visual(row['result']['visual']['raw_response'])
            self.assertIsNotNone(parsed['id_contrato'])
            self.assertIsNotNone(parsed['modalidad'])
            self.assertIsNotNone(parsed['valor_cop'])
            self.assertTrue(evidence['objeto']['observed_literals'])
        # Structural replay only, not new VLM inference or blind quality validation.

    def test_wrapped_object(self):
        out = self.transcribe('Objeto registrado: Adquirir\nequipos de oficina\nEntidad: Alcaldía\nValor del contrato (COP): 7000')
        self.assertEqual(out['objeto'], 'Adquirir equipos de oficina')
        self.assertEqual(out['valor_cop'], '7000')

    def test_missing_is_not_filled(self):
        out = self.transcribe('Identificador del contrato: CO1.PCCNTR.123')
        self.assertIsNone(out['valor_cop'])
        self.assertEqual(requested_missing('¿Qué modalidad y valor aparecen?', out), ['modalidad','valor_cop'])

    def test_missing_visual_field_blocks_generator(self):
        from final.integration import IntegratedSystem
        output = self.transcribe('Identificador del contrato: CO1.PCCNTR.123')
        class Vision:
            def extract(self, image):
                return {'output':output,'parse_error':None}
        def forbidden(*args):
            self.fail('Missing image field must not be filled from corpus')
        result = IntegratedSystem([],forbidden,vision=Vision()).predict('¿Qué valor aparece?',image=object())
        self.assertEqual(result['guard'],'missing_visual_fields')
        self.assertTrue(result['output']['abstencion'])

    def test_ambiguous_duplicate_is_null(self):
        out = self.transcribe('Modalidad: A\nModalidad: B\nValor (COP): 100')
        self.assertIsNone(out['modalidad'])

    def test_invalid_id_not_completed(self):
        out = self.transcribe('Identificador del contrato: 123\nValor (COP): 100')
        self.assertIsNone(out['id_contrato'])

    def test_instruction_echo_rejected(self):
        with self.assertRaises(ValueError):
            self.transcribe('Lee exclusivamente la ficha contractual visible.')

    def test_nonfinite_or_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            transcription_to_visual('{"legible":true,"texto_visible":"Valor (COP): 100","valor_cop":"200"}')

    def test_amounts_no_invented_magnitude(self):
        self.assertEqual(amount_literal('77.000.000 COP'), '77000000')
        self.assertEqual(amount_literal('$ 1,766,080'), '1766080')
        self.assertIsNone(amount_literal('77 millones'))
        self.assertIsNone(amount_literal('77O00000'))

    def test_tool_requires_exactly_two_ids_and_difference_of_values(self):
        a, b = 'CO1.PCCNTR.1180445', 'CO1.PCCNTR.1637043'
        self.assertTrue(eligible_difference(f'¿Diferencia absoluta de valores de {a} y {b}?'))
        for q in [f'¿Qué modalidad registra {a}?', f'¿Qué modalidad registran {a} y {b}?',
                  f'¿Diferencia de valores de {a}?', f'No calcules diferencia de valores de {a} y {b}',
                  f'Diferencia de fechas de {a} y {b}']:
            self.assertFalse(eligible_difference(q))

    def test_real_adapter_no_router_for_modality(self):
        from final.adapters import AnswerAdapter
        adapter = AnswerAdapter.__new__(AnswerAdapter)
        class Retriever:
            def search(self, q, k):
                return [{'doc_id':'CO1.PCCNTR.123','chunk_id':'c','text':'Modalidad: A'}]
        class Generator:
            calls = 0
            def generate(self, system, user):
                self.calls += 1
                return '{"respuesta":"A","explicacion":"Fuente","citas":["c"],"abstencion":false}'
        adapter.retriever, adapter.generator, adapter.tools = Retriever(), Generator(), object()
        result = adapter('¿Qué modalidad registra CO1.PCCNTR.123?')
        self.assertEqual(result['tool_calls'], 0)
        self.assertEqual(adapter.generator.calls, 1)
        self.assertEqual(result['tool_policy'], 'not_eligible_no_router')

    def test_blank_pixel_guard_does_not_need_model(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow optional in pure CPU test environment')
        from final.adapters import Vision
        vision = Vision.__new__(Vision)
        for color in ('white','black'):
            result = vision.extract(Image.new('RGB',(100,100),color))
            self.assertFalse(result['vision_model_used'])
            self.assertFalse(result['output']['legible'])
            self.assertIsNone(result['raw_response'])


if __name__ == '__main__':
    unittest.main()
