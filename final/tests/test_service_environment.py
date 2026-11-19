import importlib.metadata
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from final.service_environment import EXPECTED, inspect_environment, package_versions, require_environment
from final.run_service_preflight import run


class EnvironmentTests(unittest.TestCase):
    def test_requirements_sdk_and_checker_are_one_configuration(self):
        from packaging.requirements import Requirement
        from packaging.version import Version
        lines = (ROOT/'final/space_candidate/requirements.txt').read_text().splitlines()
        requirements = [Requirement(line) for line in lines if line.strip() and not line.startswith('#')]
        actual = {r.name: str(r.specifier)[2:] for r in requirements if not r.marker or r.marker.evaluate()}
        self.assertEqual(actual, EXPECTED)
        self.assertIn('sdk_version: '+EXPECTED['gradio'], (ROOT/'final/space_candidate/README.md').read_text(encoding='utf-8'))
        self.assertEqual(str(Version(EXPECTED['huggingface-hub'])), '0.36.2')

    def test_missing_package_is_reported_not_metadata_crash(self):
        def version(name):
            if name == 'chromadb': raise importlib.metadata.PackageNotFoundError(name)
            return EXPECTED.get(name, '2.8.0')
        with patch('importlib.metadata.version', side_effect=version), patch('importlib.metadata.requires', return_value=[]):
            report = inspect_environment()
        self.assertFalse(report['ready'])
        self.assertEqual(report['missing'], ['chromadb'])
        self.assertIsNone(report['packages']['chromadb'])

    def test_original_gradio_hub_conflict_detected_without_model_import(self):
        versions = dict(EXPECTED, torch='2.8.0', gradio='6.32.0')
        def requirements(name):
            return ['huggingface-hub>=1.16.0,<3.0'] if name == 'gradio' else []
        with patch('final.service_environment.package_versions', return_value=versions), patch('importlib.metadata.requires', side_effect=requirements):
            report = inspect_environment()
            with self.assertRaises(RuntimeError): require_environment()
        self.assertEqual(report['mismatched'], ['gradio'])
        self.assertEqual(report['conflicts'][0]['package'], 'gradio')

    def test_compatible_pins_pass(self):
        versions = dict(EXPECTED, torch='2.8.0')
        def requirements(name):
            return ['huggingface-hub>=0.33.5,<2'] if name == 'gradio' else []
        with patch('final.service_environment.package_versions', return_value=versions), patch('importlib.metadata.requires', side_effect=requirements):
            self.assertTrue(require_environment()['ready'])

    def test_failure_before_payload_still_writes_metadata(self):
        report = {'ready': False, 'packages': {'chromadb': None}, 'missing': ['chromadb']}
        with tempfile.TemporaryDirectory() as folder, patch('final.service_environment.inspect_environment', return_value=report):
            output = Path(folder)/'results'
            with self.assertRaises(RuntimeError): run(Path(folder)/'absent_candidate', output)
            metadata = json.loads((output/'metadata.json').read_text())
            self.assertEqual(metadata['status'], 'failed_partial_evidence_retained')
            self.assertEqual(metadata['environment']['missing'], ['chromadb'])


if __name__ == '__main__': unittest.main()
