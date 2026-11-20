import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from final.visual_deployment18 import load_protocol, diagnose, IDS, PROTOCOL


class Visual18Tests(unittest.TestCase):
    def test_frozen_eight_cases_and_source_fingerprints(self):
        p = load_protocol()
        self.assertEqual([c['id'] for c in p['cases']], IDS)
        self.assertEqual(sum(c['is_control'] for c in p['cases']), 3)
        self.assertTrue(p['post_hoc'])
        self.assertEqual(p['policy']['new_api_calls'], 0)
        self.assertFalse(p['policy']['model_prompt_changes'])

    def test_altered_fixture_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as folder:
            for source in PROTOCOL.iterdir():
                if source.is_file(): shutil.copyfile(source, Path(folder)/source.name)
            (Path(folder)/'blank.png').write_bytes(b'changed')
            with self.assertRaises(ValueError): load_protocol(folder)

    def test_correct_read_and_literal_answer_not_human_approval(self):
        case = load_protocol()['cases'][1]
        visual = case['expected_for_diagnostics_only']
        record = {'visual': {'output': visual}, 'output': {'respuesta': visual['modalidad']+'; 250.000.000 COP.',
                  'citas': ['IMAGE::input'], 'abstencion': False}, 'guard': None}
        d = diagnose(case, record)
        self.assertTrue(d['usable_legible_case_automatic_only'])
        self.assertIsNone(d['human_semantic_approval'])

    def test_extra_zero_is_not_a_correct_read_even_if_blocked(self):
        case = load_protocol()['cases'][0]
        visual = dict(case['expected_for_diagnostics_only'], valor_cop='2500000000')
        record = {'visual': {'output': visual}, 'output': {'respuesta': 'No dispongo de evidencia',
                  'citas': [], 'abstencion': True}, 'guard': 'visual_source_conflict'}
        d = diagnose(case, record)
        self.assertFalse(d['all_expected_visual_fields_exact'])
        self.assertTrue(d['ocr_error_blocked'])
        self.assertFalse(d['usable_legible_case_automatic_only'])

    def test_wrong_read_answered_is_flagged(self):
        case = load_protocol()['cases'][0]
        record = {'visual': {'output': {}}, 'output': {'respuesta': 'Dato', 'abstencion': False}}
        self.assertTrue(diagnose(case, record)['potential_unsafe_answer_requires_review'])

    def test_control_abstention_not_counted_as_legible_success(self):
        case = load_protocol()['cases'][-1]
        record = {'visual': {'output': {'legible': False}}, 'output': {'abstencion': True}, 'guard': 'unreadable'}
        d = diagnose(case, record)
        self.assertTrue(d['control_protected'])
        self.assertTrue(d['expected_guard_exact'])
        self.assertFalse(d['usable_legible_case_automatic_only'])

    def fake_runtime(self):
        row = {'output': {'respuesta': 'No dispongo de evidencia', 'explicacion': 'Prueba simulada',
                          'abstencion': True, 'citas': []}, 'contexts': [], 'visual': None,
               'components': {}, 'tool_trace': [], 'latency_seconds': 0.01}
        return types.SimpleNamespace(predict=Mock(return_value=row),
            model_state=lambda: {'fake_test_only': True}, index_probe=lambda: True)

    def test_runner_one_pass_no_expected_fields_in_inference(self):
        from final.visual_deployment18 import run
        runtime = self.fake_runtime()
        torch = types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda: True, get_device_name=lambda n: 'Tesla T4'))
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {'torch': torch}), \
                patch('final.service_environment.require_environment', return_value={'ready': True}), \
                patch('final.service_runtime.load_runtime', return_value=runtime), contextlib.redirect_stdout(io.StringIO()):
            meta = run(Path(folder)/'results')
            self.assertEqual(meta['status'], 'completed_requires_review')
            self.assertEqual(runtime.predict.call_count, 8)
            self.assertEqual(meta['api_calls'], 0)
            self.assertFalse(meta['deployment_quality_approved'])
            self.assertTrue(all(set(c.kwargs) == {'image'} for c in runtime.predict.call_args_list))

    def test_runner_stops_and_preserves_partial_without_retry(self):
        from final.visual_deployment18 import run
        runtime = self.fake_runtime()
        row = runtime.predict.return_value
        runtime.predict.side_effect = [row, row, RuntimeError('test failure')]
        torch = types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda: True, get_device_name=lambda n: 'Tesla T4'))
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {'torch': torch}), \
                patch('final.service_environment.require_environment', return_value={'ready': True}), \
                patch('final.service_runtime.load_runtime', return_value=runtime), contextlib.redirect_stdout(io.StringIO()):
            output = Path(folder)/'results'
            with self.assertRaises(RuntimeError): run(output)
            meta = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'], 'failed_partial_evidence_retained')
            self.assertEqual(meta['completed_cases'], 2)
            self.assertEqual(runtime.predict.call_count, 3)


if __name__ == '__main__': unittest.main()
