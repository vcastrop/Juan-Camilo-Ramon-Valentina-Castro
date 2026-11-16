from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.run_integration import fixture_font_path


class FixtureTests(unittest.TestCase):
    def test_resolves_packaged_font_without_system_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)/'matplotlib'
            font = package/'mpl-data/fonts/ttf/DejaVuSans.ttf'
            font.parent.mkdir(parents=True)
            font.touch()
            with patch('importlib.util.find_spec', return_value=SimpleNamespace(origin=str(package/'__init__.py'))):
                self.assertEqual(fixture_font_path(), font)

    def test_missing_dependency_explicit(self):
        with patch('importlib.util.find_spec', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'requirements-integration'):
                fixture_font_path()


if __name__ == '__main__':
    unittest.main()
