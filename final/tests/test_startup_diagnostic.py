import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import contextlib
import io

from final.startup_diagnostic_patch import startup_diagnostic,patch_app
from final.build_space_ocr import render_app

ROOT=Path(__file__).resolve().parents[2]


class StartupDiagnosticTests(unittest.TestCase):
    def test_meta_failure_identified_without_retaining_private_message(self):
        try:raise NotImplementedError('Cannot copy out of meta tensor SECRET_PRIVATE_TOKEN /private/path')
        except Exception as error:result=startup_diagnostic(error)
        self.assertEqual(result['reason_code'],'meta_tensor_materialization')
        self.assertNotIn('SECRET',json.dumps(result))
        self.assertNotIn('/private',json.dumps(result))
        self.assertTrue(result['frames'])

    def test_unknown_error_not_invented(self):
        self.assertEqual(startup_diagnostic(ValueError('private body'))['reason_code'],'unclassified_startup_exception')

    def test_real_template_failure_prints_safe_diagnostic_and_stays_not_ready(self):
        try: import gradio
        except ImportError:self.skipTest('Optional UI check')
        original=render_app((ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8'),
                           "def unpack(*args): return {'source_commit': SOURCE_COMMIT}",'b'*64,'a'*40)
        app=patch_app(original)
        self.assertIn("SOURCE_COMMIT = '"+'a'*40+"'",app)
        module=types.ModuleType('diagnostic_ui');module.__file__=str(ROOT/'final/space_ocr/app.py')
        stream=io.StringIO()
        with patch.dict(sys.modules,{'spaces':types.SimpleNamespace(GPU=lambda **kw:lambda fn:fn)}),patch('final.integration_ocr23.load_runtime',side_effect=ValueError('SECRET_PRIVATE')),contextlib.redirect_stdout(stream):
            exec(compile(app,module.__file__,'exec'),module.__dict__)
        try:
            self.assertIn('contractrisk_startup_diagnostic',stream.getvalue())
            self.assertNotIn('SECRET_PRIVATE',stream.getvalue())
            self.assertFalse(module.service.health()['contract_system_ready'])
            self.assertEqual(module.readyz(None).status_code,503)
        finally:module.demo.close()
