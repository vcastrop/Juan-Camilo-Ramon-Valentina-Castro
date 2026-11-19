import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from final.prepare_test_history import prepare, REQUIRED_COMMITS


class HistoryPreparationTests(unittest.TestCase):
    def test_shallow_fetch_does_not_change_checkout(self):
        with patch('subprocess.check_output', side_effect=['a'*40, 'true', 'a'*40, 'false']), patch('subprocess.run') as command:
            result = prepare(ROOT)
        calls = [c.args[0] for c in command.call_args_list]
        self.assertEqual(calls[0], ['git', 'fetch', '--unshallow', 'origin', 'Entrega/contractrisk-final'])
        self.assertEqual(len(calls), 1+len(REQUIRED_COMMITS))
        self.assertTrue(result['checkout_unchanged'])

    def test_full_checkout_needs_no_network_fetch(self):
        with patch('subprocess.check_output', side_effect=['a'*40, 'false', 'a'*40, 'false']), patch('subprocess.run') as command:
            result = prepare(ROOT)
        self.assertFalse(result['was_shallow'])
        self.assertTrue(all(c.args[0][1] == 'cat-file' for c in command.call_args_list))

    def test_notebook_preserves_history_and_checks_before_tests(self):
        nb = json.loads((ROOT/'final/ContractRisk_Final_Despliegue_17_Colab.ipynb').read_text(encoding='utf-8'))
        source = '\n'.join(c['source'] for c in nb['cells'] if c['cell_type']=='code')
        self.assertNotIn("'--depth'", source)
        self.assertIn("'--single-branch'", source)
        self.assertLess(source.index('final/prepare_test_history.py'), source.index("'-m','unittest'"))


if __name__ == '__main__': unittest.main()
