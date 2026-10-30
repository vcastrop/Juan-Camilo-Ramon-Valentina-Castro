import sys
import unittest
import hashlib
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_corpus import TYPES, documents, select_records


def row(identity, kind, text=None):
    return {'id_contrato': identity, 'tipo_de_contrato': kind,
            'descripcion_del_proceso': text or f'Descripción sintética de prueba suficientemente larga para {identity}'}


class CorpusTests(unittest.TestCase):
    def test_snapshot_integrity_and_portable_line_endings(self):
        corpus = Path(__file__).resolve().parents[1] / 'corpus'
        manifest = json.loads((corpus / 'manifest.json').read_text(encoding='utf-8'))
        for name, expected in manifest['files'].items():
            data = (corpus / name).read_bytes()
            self.assertNotIn(b'\r\n', data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected)

    def test_preserves_source_text_and_does_not_invent_missing_fields(self):
        source = row('TEST-1', 'Obra')
        doc = documents([source])[0]
        self.assertIn(source['descripcion_del_proceso'], doc['text'])
        self.assertNotIn('Valor del contrato', doc['text'])
        self.assertEqual(doc['document_type'], 'public_contract_data_record')

    def test_forbids_unselected_personal_fields(self):
        source = row('TEST-1', 'Obra')
        source['n_mero_de_cuenta'] = 'synthetic-test'
        with self.assertRaises(ValueError):
            documents([source])

    def test_excludes_historical_ids_and_normalized_text(self):
        groups = {kind: [row(f'{i}-old', kind), row(f'{i}-text', kind, 'Una descripción histórica que debe quedar fuera del corpus.'),
                         row(f'{i}-new', kind)] for i, kind in enumerate(TYPES)}
        selected = select_records(groups, 1, {f'{i}-old' for i in range(len(TYPES))},
                                  {'una descripción histórica que debe quedar fuera del corpus.'})
        self.assertEqual([r['id_contrato'] for r in selected], [f'{i}-new' for i in range(len(TYPES))])

    def test_missing_group_does_not_get_fabricated(self):
        with self.assertRaises(ValueError):
            select_records({kind: [] for kind in TYPES}, 1, set(), set())


if __name__ == '__main__':
    unittest.main()
