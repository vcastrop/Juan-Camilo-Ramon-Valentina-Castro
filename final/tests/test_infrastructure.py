import contextlib
import ast
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

module_path = Path(__file__).resolve().parents[1] / 'space/telemetry.py'
spec = importlib.util.spec_from_file_location('technical_telemetry', module_path)
telemetry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telemetry)


class InfrastructureTests(unittest.TestCase):
    def test_native_launch_and_direct_gpu_callback(self):
        tree = ast.parse((module_path.parent / 'app.py').read_text(encoding='utf-8'))
        gpu_functions = {node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and any(
                isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                and isinstance(d.func.value, ast.Name) and d.func.value.id == 'spaces'
                and d.func.attr == 'GPU' for d in node.decorator_list)}
        callbacks = {node.args[0].id for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'click' and node.args and isinstance(node.args[0], ast.Name)}
        self.assertTrue(gpu_functions & callbacks)
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == 'uvicorn'
            for node in ast.walk(tree)))

    def test_spaces_matches_observed_zerogpu_builder(self):
        requirements = (module_path.parent / 'requirements.txt').read_text(encoding='utf-8').splitlines()
        self.assertIn('spaces==0.51.3', requirements)
        self.assertNotIn('spaces==0.52.0', requirements)

    def test_allowlist_and_json(self):
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            payload = telemetry.event('infrastructure_smoke', 0.1, True)
        self.assertEqual(json.loads(captured.getvalue()), payload)
        self.assertEqual(set(payload), {'timestamp_utc', 'request_id', 'event_type',
            'latency_seconds', 'success', 'rag_used', 'tool_used', 'vision_used',
            'gpu_probe_used', 'abstention', 'phase', 'version'})
        self.assertIsNone(payload['abstention'])
        self.assertFalse(payload['vision_used'])

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            telemetry.event('arbitrary query content', 0.1, True)

    def test_latency_rejected(self):
        for value in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                telemetry.event('gpu_smoke', value, True)

    def test_no_key_does_not_require_sdk(self):
        with patch.dict('os.environ', {}, clear=True):
            self.assertEqual(telemetry.send({}), 'disabled')


if __name__ == '__main__':
    unittest.main()
