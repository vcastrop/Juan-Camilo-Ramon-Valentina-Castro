import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from final.service_contract import Service, event, validate, validate_event, InputError
from final.service_telemetry import Telemetry
from final.service_runtime import verify_assets
from final.space_payload import unpack
from final.build_space_candidate import local_modules

VERSION = 'a'*40


class Backend:
    def model_state(self):
        return dict.fromkeys(['generator', 'vision', 'classifier', 'embedding', 'reranker'], True)
    def index_probe(self): return True
    def predict(self, question, **kwargs):
        return {'output': {'respuesta': 'public answer', 'explicacion': 'public reason', 'citas': [], 'abstencion': False},
                'components': {'rag': True, 'vision': False, 'classifier': False, 'tool': True},
                'tool_trace': [{'decision': {'action': 'tool'}, 'tool_result': {'ok': False}}],
                'contexts': [], 'question': question, 'raw_response': 'PRIVATE_TRACE'}


class ServiceTests(unittest.TestCase):
    def test_assets_pinned(self):
        self.assertEqual(len(verify_assets()), 24)

    def test_all_components_and_index_required(self):
        backend = Backend()
        service = Service(backend, VERSION)
        self.assertTrue(service.health()['contract_system_ready'])
        with patch.object(backend, 'model_state', return_value={'generator': True}):
            self.assertFalse(service.health()['contract_system_ready'])
        with patch.object(backend, 'index_probe', side_effect=RuntimeError('private path')):
            self.assertFalse(service.health()['contract_system_ready'])
        with patch.object(backend, 'model_state', side_effect=RuntimeError('private path')):
            self.assertEqual(service.health()['status'], 'alive')

    def test_absent_backend_never_fake_answer(self):
        service = Service(None, VERSION)
        display, metadata = service.compute('Pregunta', 'qa', '', None, True)
        self.assertEqual(display['error'], 'not_ready')
        self.assertFalse(metadata['success'])
        self.assertIsNone(metadata['rag_used'])

    def test_compute_has_no_private_trace_or_question(self):
        display, metadata = Service(Backend(), VERSION).compute('PRIVATE_QUESTION', 'qa', '', None, True)
        joined = json.dumps([display, metadata])
        self.assertNotIn('PRIVATE_QUESTION', joined)
        self.assertNotIn('PRIVATE_TRACE', joined)
        self.assertFalse(metadata['tool_used'])
        self.assertTrue(metadata['router_used'])
        self.assertTrue(metadata['success'])
        validate_event(metadata)

    def test_successful_tool_separate_from_router(self):
        row = Backend().predict('x')
        row['tool_trace'][0]['tool_result']['ok'] = True
        self.assertTrue(event(VERSION, 1, record=row)['tool_used'])

    def test_input_limits_and_consent(self):
        for q, mode, desc, consent in [('x', 'qa', '', False), ('', 'qa', '', True),
                ('x'*1201, 'qa', '', True), ('x', 'qa', 'x'*8001, True),
                ('', 'sufficiency', '', True), ('x', 'evil', '', True)]:
            with self.assertRaises(InputError): validate(q, mode, desc, None, consent)
        self.assertTrue(validate('', 'sufficiency', 'text', None, True))

    def test_pixel_limit_and_type(self):
        from PIL import Image
        with self.assertRaises(InputError): validate('q', 'qa', '', object(), True)
        with Image.new('RGB', (4000, 3001)) as image:
            with self.assertRaises(InputError): validate('q', 'qa', '', image, True)

    def test_runtime_failure_sanitized(self):
        backend = Backend()
        with patch.object(backend, 'predict', side_effect=RuntimeError('SECRET /private/path')):
            display, payload = Service(backend, VERSION).compute('x', 'qa', '', None, True)
        self.assertEqual(payload['error_code'], 'runtime_error')
        self.assertNotIn('SECRET', json.dumps(display))

    def test_verified_only_after_parent_observation(self):
        service = Service(Backend(), VERSION)
        _, payload = service.compute('x', 'qa', '', None, True)
        self.assertFalse(service.health()['real_request_verified'])
        service.observe_finished(payload)
        self.assertTrue(service.health()['real_request_verified'])

    def test_telemetry_rejects_content_before_print(self):
        baseline = event(VERSION, 1)
        mutations = [{'question': 'PRIVATE'}, {'mode': 'PRIVATE'}, {'version': 'PRIVATE'},
                     {'timestamp_utc': 'PRIVATE'}, {'request_id': 'PRIVATE'}, {'rag_used': 'PRIVATE'},
                     {'success': 'PRIVATE'}, {'latency_seconds': float('nan')}]
        for change in mutations:
            with self.subTest(change=change), contextlib.redirect_stdout(io.StringIO()) as stream:
                with self.assertRaises((ValueError, TypeError)):
                    Telemetry().send(dict(baseline, **change))
                self.assertEqual(stream.getvalue(), '')

    def test_without_key_inference_and_metadata_available(self):
        with patch.dict('os.environ', {'WANDB_API_KEY': ''}), contextlib.redirect_stdout(io.StringIO()) as stream:
            status = Telemetry().send(event(VERSION, 1))
        self.assertEqual(status, 'disabled')
        self.assertEqual(json.loads(stream.getvalue())['version'], VERSION)

    def test_wandb_only_numeric_metadata_no_stdout_capture(self):
        fake = types.SimpleNamespace(init=unittest.mock.Mock(), Settings=unittest.mock.Mock())
        with patch.dict('os.environ', {'WANDB_API_KEY': 'fake_test_not_real'}), patch.dict(sys.modules, {'wandb': fake}), contextlib.redirect_stdout(io.StringIO()):
            telemetry = Telemetry()
            self.assertEqual(telemetry.send(event(VERSION, 2, record=Backend().predict('PRIVATE'))), 'queued_check_dashboard')
        values = fake.init.return_value.log.call_args.args[0]
        self.assertTrue(all(type(v) in {int, float} for v in values.values()))
        self.assertFalse(values['usage/tool_used'])
        self.assertEqual(fake.Settings.call_args.kwargs['console'], 'off')


class PayloadTests(unittest.TestCase):
    def archive(self, root, files, manifest_override=None):
        archive = root/'test.zip'
        manifest = {'files': {n: hashlib.sha256(v).hexdigest() for n, v in files.items()}}
        if manifest_override: manifest = manifest_override
        with zipfile.ZipFile(archive, 'w') as z:
            for name, data in files.items(): z.writestr(name, data)
            z.writestr('manifest.json', json.dumps(manifest))
        return archive, hashlib.sha256(archive.read_bytes()).hexdigest()

    def test_good_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive, sha = self.archive(root, {'final/a.py': b'x=1'})
            unpack(archive, sha, root/'out')
            self.assertEqual((root/'out/final/a.py').read_bytes(), b'x=1')

    def test_bad_sha_rejected_before_extract(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive, _ = self.archive(root, {'a': b'1'})
            with self.assertRaises(ValueError): unpack(archive, '0'*64, root/'out')
            self.assertFalse((root/'out').exists())

    def test_traversal_and_manifest_tamper_rejected(self):
        for name in ['../escape', '/absolute', 'a\\b', 'C:escape']:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                archive, sha = self.archive(root, {name: b'1'})
                with self.assertRaises(ValueError): unpack(archive, sha, root/'out')
                self.assertFalse((root/'out').exists())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive, sha = self.archive(root, {'a': b'1'}, {'files': {'a': '0'*64}})
            with self.assertRaises(ValueError): unpack(archive, sha, root/'out')

    def test_dependency_closure_does_not_ship_judge_or_eval(self):
        names = local_modules(['final/service_runtime.py', 'final/service_contract.py', 'final/service_telemetry.py'])
        self.assertIn('m3/sqlite_support.py', names)
        self.assertIn('final/visual_fields.py', names)
        self.assertIn('m3/agent_v5.py', names)
        self.assertFalse(any(any(word in n for word in ['judge', 'harness', '/tests/', 'eval_set', '/evidence/']) for n in names))
        self.assertTrue(all(n.endswith('.py') for n in names))
        self.assertTrue(all((ROOT/n).is_file() for n in names))

    def test_ui_builds_with_gradio6_and_fake_backend(self):
        try: import gradio
        except ImportError: self.skipTest('Optional Gradio compatibility check')
        template = (ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8')
        template = template.replace('# __BOOTSTRAP__', "def unpack(*args): return {'source_commit': SOURCE_COMMIT}")
        template = template.replace('__SOURCE_COMMIT__', VERSION)
        module = types.ModuleType('candidate_ui_test')
        module.__file__ = str(ROOT/'final/space_candidate/app.py')
        fake_spaces = types.SimpleNamespace(GPU=lambda **kwargs: lambda fn: fn)
        with patch.dict(sys.modules, {'spaces': fake_spaces}), patch('final.service_runtime.load_runtime', return_value=Backend()):
            exec(compile(template, module.__file__, 'exec'), module.__dict__)
        try:
            self.assertTrue(module.state()['contract_system_ready'])
            self.assertEqual(module.readyz(None).status_code, 200)
            self.assertEqual(module.healthz(None).status_code, 200)
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from starlette.routing import Route
            with TestClient(FastAPI(routes=[Route('/healthz', module.healthz), Route('/readyz', module.readyz)])) as client:
                self.assertEqual(client.get('/readyz').status_code, 200)
                self.assertEqual(client.get('/healthz').json()['status'], 'alive')
            module.service.backend = None
            self.assertEqual(module.readyz(None).status_code, 503)
            dependencies = module.demo.get_config_file()['dependencies']
            self.assertTrue(any(d.get('trigger_only_on_failure') for d in dependencies))
            with patch.object(module.demo, 'launch', return_value='fake') as launch:
                self.assertEqual(module.launch(), 'fake')
                self.assertFalse(launch.call_args.kwargs['ssr_mode'])
                self.assertFalse(launch.call_args.kwargs['run_history'])
        finally:
            module.demo.close()

    def test_ui_boot_failure_alive_but_not_ready(self):
        try: import gradio
        except ImportError: self.skipTest('Optional Gradio compatibility check')
        template = (ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8')
        template = template.replace('# __BOOTSTRAP__', "def unpack(*args): return {'source_commit': SOURCE_COMMIT}")
        template = template.replace('__SOURCE_COMMIT__', VERSION)
        module = types.ModuleType('candidate_failure_test')
        module.__file__ = str(ROOT/'final/space_candidate/app.py')
        fake_spaces = types.SimpleNamespace(GPU=lambda **kwargs: lambda fn: fn)
        with patch.dict(sys.modules, {'spaces': fake_spaces}), patch('final.service_runtime.load_runtime', side_effect=RuntimeError('PRIVATE_PATH')), contextlib.redirect_stdout(io.StringIO()) as stream:
            exec(compile(template, module.__file__, 'exec'), module.__dict__)
        try:
            self.assertNotIn('PRIVATE_PATH', stream.getvalue())
            self.assertEqual(module.readyz(None).status_code, 503)
            self.assertEqual(module.healthz(None).status_code, 200)
        finally: module.demo.close()


if __name__ == '__main__': unittest.main()
