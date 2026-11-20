from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from final.build_space_candidate import local_modules
from final.build_space_ocr import render_app
from final.service_ocr import OCRService,EVALUATED_LANGUAGES
from final.tests.test_service_candidate import Backend,VERSION

ROOT=Path(__file__).resolve().parents[2]


class OCRBackend(Backend):
    def model_state(self):return dict.fromkeys(['generator','classifier','embedding','reranker'],True)
    def reader_state(self):
        return {'kind':'tesseract_cpu_not_qwen_vlm','ready':True,'version':'tesseract 5.3.4',
                'language_data_sha256':EVALUATED_LANGUAGES}


class SpaceOCRTests(unittest.TestCase):
    def test_ui_routes_with_mock_runtime_then_not_ready(self):
        try: import gradio
        except ImportError:self.skipTest('Optional UI check')
        from fastapi.testclient import TestClient
        from starlette.applications import Starlette
        from starlette.routing import Route
        app=render_app((ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8'),
                       "def unpack(*args): return {'source_commit': SOURCE_COMMIT}",'b'*64,VERSION)
        module=types.ModuleType('ocr22_ui_test');module.__file__=str(ROOT/'final/space_ocr/app.py')
        with patch.dict(sys.modules,{'spaces':types.SimpleNamespace(GPU=lambda **kw:lambda fn:fn)}),patch('final.integration_ocr20.load_runtime',return_value=OCRBackend()):
            exec(compile(app,module.__file__,'exec'),module.__dict__)
        try:
            with TestClient(Starlette(routes=[Route('/healthz',module.healthz),Route('/readyz',module.readyz)])) as client:
                self.assertEqual(client.get('/readyz').status_code,200)
                self.assertEqual(len(client.get('/healthz').json()['models_loaded']),4)
                module.service.backend=None
                self.assertEqual(client.get('/readyz').status_code,503)
                self.assertEqual(client.get('/healthz').status_code,200)
        finally:module.demo.close()

    def test_four_neural_models_and_real_reader_required(self):
        backend=OCRBackend();service=OCRService(backend,VERSION)
        health=service.health()
        self.assertTrue(health['contract_system_ready'])
        self.assertEqual(len(health['models_loaded']),4)
        self.assertFalse(health['vlm_loaded'])
        self.assertTrue(health['evaluated_language_data_match'])
        with patch.object(backend,'reader_state',return_value={}):
            self.assertFalse(service.health()['contract_system_ready'])
            self.assertEqual(service.compute('q','qa','',None,True)[0]['error'],'not_ready')
        with patch.object(backend,'model_state',return_value={'generator':True}):
            self.assertFalse(service.health()['contract_system_ready'])
        with patch.object(backend,'index_probe',return_value=False):
            self.assertFalse(service.health()['contract_system_ready'])

    def test_absent_backend_and_bad_reader_are_not_fake_ready(self):
        self.assertFalse(OCRService(None,VERSION).health()['contract_system_ready'])
        backend=OCRBackend()
        with patch.object(backend,'reader_state',side_effect=RuntimeError('private')):
            self.assertNotIn('private',str(OCRService(backend,VERSION).health()))

    def test_environment_difference_is_visible_not_claimed_equivalent(self):
        backend=OCRBackend();reading=backend.reader_state()
        reading['language_data_sha256']={'spa':'different','eng':'different'}
        with patch.object(backend,'reader_state',return_value=reading):
            health=OCRService(backend,VERSION).health()
            self.assertFalse(health['evaluated_language_data_match'])
            self.assertIn('separate smoke',health['reference_evaluation_environment'])

    def test_render_preserves_gpu_and_privacy_boundary(self):
        app=render_app((ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8'),
                       (ROOT/'final/space_payload.py').read_text(encoding='utf-8'),'b'*64,VERSION)
        compile(app,'generated.py','exec')
        self.assertIn('from final.integration_ocr20 import load_runtime',app)
        self.assertIn('from final.service_ocr import OCRService as Service',app)
        self.assertIn('@spaces.GPU(duration=120)',app)
        self.assertEqual(app.count('launch()'),1)
        self.assertNotIn('__BOOTSTRAP__',app)
        self.assertNotIn('seis fallos',app)

    def test_minimal_payload_does_not_import_gold_judge_or_api(self):
        names=local_modules(['final/integration_ocr20.py','final/service_ocr.py','final/service_telemetry.py'])
        self.assertIn('final/ocr_candidate19.py',names)
        self.assertIn('final/integration_ocr20.py',names)
        for name in names:
            self.assertFalse(any(part in name for part in ['judge','evaluation','evidence/','tests/']))
        requirements=(ROOT/'final/space_candidate/requirements.txt').read_text()
        self.assertNotIn('spaces==',requirements)
        self.assertNotIn('bitsandbytes',requirements)
