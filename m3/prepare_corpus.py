"""Build a source-attributed corpus of public SECOP II records, not full contracts.

Uses Python standard library only. The frozen snapshot is the reproducibility
input; a new API download is a new capture and may contain changed source data.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
API = 'https://www.datos.gov.co/resource/jbjy-vk9h.json'
METADATA_URL = 'https://www.datos.gov.co/api/views/jbjy-vk9h.json'
FIELDS = {
    'id_contrato': 'Identificador del contrato',
    'nombre_entidad': 'Entidad',
    'departamento': 'Departamento',
    'ciudad': 'Ciudad',
    'referencia_del_contrato': 'Referencia',
    'descripcion_del_proceso': 'Descripción del proceso',
    'objeto_del_contrato': 'Objeto registrado',
    'tipo_de_contrato': 'Tipo de contrato',
    'modalidad_de_contratacion': 'Modalidad de contratación',
    'estado_contrato': 'Estado registrado en la captura',
    'fecha_de_firma': 'Fecha de firma registrada',
    'fecha_de_inicio_del_contrato': 'Fecha de inicio registrada',
    'fecha_de_fin_del_contrato': 'Fecha de fin registrada',
    'duraci_n_del_contrato': 'Duración registrada',
    'valor_del_contrato': 'Valor del contrato (COP)',
    'urlproceso': 'Enlace al proceso',
}
TYPES = ['Obra', 'Suministros', 'Compraventa', 'Consultoría',
         'Arrendamiento de inmuebles', 'Prestación de servicios']


def fetch(url):
    with urlopen(url, timeout=60) as response:
        return json.load(response)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text):
    return ' '.join(str(text).lower().split())


def historical_exclusions():
    ids, texts = set(), set()
    for rel in ['data/contractrisk_train.csv', 'data/contractrisk_validation.csv',
                'm2/eval/contractrisk_m2_eval_gold.csv']:
        with (ROOT / rel).open(encoding='utf-8-sig', newline='') as handle:
            for row in csv.DictReader(handle):
                ids.add(row['id_contrato'])
                text = row.get('descripcion_del_proceso') or row.get('text')
                if text:
                    texts.add(norm(text))
    return ids, texts


def select_records(groups, per_type, excluded_ids, excluded_texts):
    selected, seen_ids, seen_texts = [], set(excluded_ids), set(excluded_texts)
    for kind in TYPES:
        count = 0
        for row in groups[kind]:
            identity = row.get('id_contrato')
            text = norm(row.get('descripcion_del_proceso', ''))
            if not identity or len(text) < 30 or identity in seen_ids or text in seen_texts:
                continue
            selected.append({key: row[key] for key in FIELDS if key in row})
            seen_ids.add(identity)
            seen_texts.add(text)
            count += 1
            if count == per_type:
                break
        if count != per_type:
            raise ValueError(f'{kind}: only {count} usable rows; required {per_type}. No substitutes invented.')
    return selected


def documents(records):
    output = []
    for row in records:
        unexpected = set(row) - set(FIELDS)
        if unexpected:
            raise ValueError(f'Unexpected source fields: {sorted(unexpected)}')
        lines = []
        for key, label in FIELDS.items():
            if key == 'urlproceso':
                continue
            value = row.get(key)
            if value is not None and str(value).strip():
                lines.append(f'{label}: {value}')
        process_url = row.get('urlproceso', {})
        if isinstance(process_url, dict):
            process_url = process_url.get('url', '')
        output.append({
            'doc_id': row['id_contrato'], 'source_dataset': 'jbjy-vk9h',
            'source_url': API + '?' + urlencode({'$where': "id_contrato='" + row['id_contrato'] + "'"}),
            'process_url': process_url, 'document_type': 'public_contract_data_record',
            'text': '\n'.join(lines),
        })
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-types', action='store_true')
    parser.add_argument('--snapshot', type=Path, help='Rebuild from a frozen JSON snapshot, without network')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'm3/corpus')
    parser.add_argument('--per-type', type=int, default=4)
    args = parser.parse_args()
    if args.list_types:
        print(canonical(fetch(API + '?' + urlencode({'$select': 'tipo_de_contrato,count(*) AS n',
              '$group': 'tipo_de_contrato', '$order': 'n DESC'}))))
        return
    if args.per_type < 1:
        parser.error('--per-type must be positive')
    out = args.output_dir
    if out.exists() and any(out.iterdir()):
        parser.error('Output directory must be empty/new to preserve existing captures.')
    if args.snapshot:
        capture = json.loads(args.snapshot.read_text(encoding='utf-8'))
    else:
        meta = fetch(METADATA_URL)
        groups, urls = {}, []
        for kind in TYPES:
            query = {'$select': ','.join(FIELDS),
                     '$where': "tipo_de_contrato='" + kind.replace("'", "''") + "' AND fecha_de_firma >= '2024-01-01T00:00:00' AND fecha_de_firma < '2025-01-01T00:00:00'",
                     '$order': 'id_contrato ASC', '$limit': '80'}
            url = API + '?' + urlencode(query)
            print('Downloading:', kind, flush=True)
            groups[kind] = fetch(url)
            urls.append(url)
        ids, texts = historical_exclusions()
        records = select_records(groups, args.per_type, ids, texts)
        capture = {
            'schema_version': '1.0', 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
            'metadata_url': METADATA_URL, 'dataset_metadata': {
                k: meta.get(k) for k in ['name', 'attribution', 'attributionLink', 'licenseId', 'license', 'description']},
            'selection': {'year': 2024, 'per_type': args.per_type, 'types': TYPES,
                          'method': 'First usable unique records by id within each type; purposive, not representative',
                          'excluded_historical_ids_count': len(ids), 'queries': urls},
            'records': records,
        }
    docs = documents(capture['records'])
    ids, texts = historical_exclusions()
    overlap = [r['id_contrato'] for r in capture['records']
               if r['id_contrato'] in ids or norm(r.get('descripcion_del_proceso', '')) in texts]
    if overlap:
        raise ValueError(f'Historical overlap: {overlap}')
    if len({d['doc_id'] for d in docs}) != len(docs):
        raise ValueError('Duplicate document identifiers')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'source_snapshot.json').write_text(canonical(capture), encoding='utf-8')
    (out / 'documents.jsonl').write_text(''.join(json.dumps(d, ensure_ascii=False, sort_keys=True) + '\n' for d in docs), encoding='utf-8')
    manifest = {
        'status': 'candidate_corpus_pending_team_review', 'documents': len(docs),
        'historical_id_or_exact_normalized_description_overlap': overlap,
        'types': dict(Counter(r['tipo_de_contrato'] for r in capture['records'])),
        'word_counts': {'min': min(len(d['text'].split()) for d in docs),
                        'max': max(len(d['text'].split()) for d in docs)},
        'files': {name: digest(out / name) for name in ['source_snapshot.json', 'documents.jsonl']},
        'limitations': ['Data records, not full contracts or procurement annexes.',
                       'No fraud/irregularity ground truth.', 'Purposive small sample, not population-representative.',
                       'Source missing/placeholder fields are not verified facts.'],
    }
    (out / 'manifest.json').write_text(canonical(manifest), encoding='utf-8')
    print(canonical(manifest))


if __name__ == '__main__':
    main()
