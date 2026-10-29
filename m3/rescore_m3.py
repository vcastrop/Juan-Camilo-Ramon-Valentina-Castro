"""Re-score a saved final run with m3-harness-1.1. Usage: rescore_m3.py RUN_DIR OUTPUT_DIR

Reads harness_rows.jsonl only; never regenerates answers or judge notes. OUTPUT_DIR must be new.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from harness_m3_v11 import HARNESS_VERSION, RULES, rescore, scorecard
from run_final_m3 import load_gold
from sistemas_m3 import ABLATIONS, LABELS, MAIN

CARD_COLUMNS = ['variant', 'label', 'cases', 'valid_outputs', 'dim1_fact_coverage', 'dim1_complete_answers',
                'dim2_judge_mean', 'dim2_judge_valid', 'dim3_domain_passed', 'dim3_domain_rate',
                'm2_compatible_rate', 'unanswerable_abstained', 'unanswerable_total',
                'evidence_retrieved_mean', 'evidence_retrieved_complete', 'evidence_with_tool_complete',
                'answerable_total', 'latency_median_seconds', 'system_errors', 'harness_version']
CASE_COLUMNS = ['variant', 'eval_id', 'kind', 'valid_output', 'coverage', 'v10_accuracy', 'facts_missing',
                'judge_score', 'domain_pass', 'v10_domain_pass', 'domain_reasons', 'm2_compatible_pass',
                'evidence_retrieved', 'evidence_with_tool', 'latency_seconds']


def fmt(v, digits=3):
    return 'N/A' if v is None else (f'{v:.{digits}f}' if isinstance(v, float) else str(v))


def write_csv(path, columns, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                        for k, v in r.items()})


def build(run_dir, output):
    gold = {c['eval_id']: c for c in load_gold()}
    source = run_dir/'harness_rows.jsonl'
    items = [json.loads(l) for l in source.read_text(encoding='utf-8').splitlines() if l.strip()]
    rows = [rescore(gold[i['row']['eval_id']], i) for i in items]
    variants = [v for v in MAIN+ABLATIONS if any(r['variant'] == v for r in rows)]
    cards = [dict(scorecard([r for r in rows if r['variant'] == v]), variant=v, label=LABELS[v]) for v in variants]
    output.mkdir(parents=True)
    write_csv(output/'scorecard_m3_v1_1.csv', CARD_COLUMNS, cards)
    write_csv(output/'scorecard_casos_m3_v1_1.csv', CASE_COLUMNS, rows)
    lines = ['| Sistema | Dim. 1 cobertura de hechos (0-1) | Respuestas con cobertura completa | Dim. 2 juez (1-5) | Dim. 3 chequeo de dominio | Latencia mediana (s) |',
             '|---|---:|---:|---:|---:|---:|']
    lines += [f"| {c['label']} | {fmt(c['dim1_fact_coverage'])} | {c['dim1_complete_answers']}/{c['cases']} | "
              f"{fmt(c['dim2_judge_mean'], 2)} | {c['dim3_domain_passed']}/{c['cases']} | {fmt(c['latency_median_seconds'], 2)} |"
              for c in cards]
    lines += ['', '| Sistema | Hechos requeridos en fragmentos recuperados (media) | Casos con todos los hechos recuperados | Con resultado de herramienta |',
              '|---|---:|---:|---:|']
    lines += [f"| {c['label']} | {fmt(c['evidence_retrieved_mean'])} | {c['evidence_retrieved_complete']}/{c['answerable_total']} | "
              f"{c['evidence_with_tool_complete']}/{c['answerable_total']} |" for c in cards]
    (output/'tablas_m3_v1_1.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    meta = {'harness_version': HARNESS_VERSION, 'rules': RULES, 'created_utc': datetime.now(timezone.utc).isoformat(),
            'source_run': str(run_dir), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'regenerated_answers': False, 'regenerated_judgements': False,
            'changed_vs_v1_0': [r['variant']+'/'+r['eval_id'] for r in rows
                                if r['coverage'] != r['v10_accuracy'] or r['domain_pass'] != r['v10_domain_pass']]}
    (output/'metadata.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    return '\n'.join(lines), meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output folder; previous evidence must be preserved')
    table, meta = build(args.run_dir, args.output)
    print(table)
    print('Cambios frente a 1.0:', meta['changed_vs_v1_0'])
