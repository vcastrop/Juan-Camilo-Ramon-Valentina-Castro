"""Recompute every table from per-case detail and export CSV + Markdown. Usage: report_m3.py RESULTS_DIR"""
import argparse
import csv
import json
from pathlib import Path
from harness_m3 import scorecard
from ragas_m3 import APPLICABILITY, summarize
from sistemas_m3 import ABLATIONS, LABELS, MAIN

SCORE_COLUMNS = ['variant', 'label', 'cases', 'valid_outputs', 'dim1_accuracy', 'dim2_judge_mean',
                 'dim2_judge_valid', 'dim3_domain_rate', 'dim3_domain_passed', 'm2_compatible_rate',
                 'similarity_mean', 'unanswerable_abstained', 'unanswerable_total',
                 'latency_median_seconds', 'latency_cases', 'system_errors', 'harness_version']
CASE_COLUMNS = ['variant', 'eval_id', 'kind', 'valid_output', 'accuracy', 'judge_score', 'domain_pass',
                'domain_reasons', 'm2_compatible_pass', 'similarity', 'latency_seconds', 'abstencion',
                'tool_calls', 'termination', 'cited', 'retrieved_docs', 'respuesta', 'judge_reason']


def read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]


def fmt(value, digits=3):
    if value is None:
        return 'N/A'
    return f'{value:.{digits}f}' if isinstance(value, float) else str(value)


def write_csv(path, columns, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})


def case_row(item):
    row, record, judgement = item['row'], item['record'], item.get('judgement') or {}
    output = record.get('output') or {}
    return dict(row, abstencion=output.get('abstencion'), respuesta=output.get('respuesta'),
                cited=output.get('citas'), tool_calls=record.get('tool_calls'),
                termination=record.get('termination'), judge_reason=judgement.get('reason'),
                retrieved_docs=sorted({c['doc_id'] for c in record.get('contexts', [])}))


def build(results):
    items = read_jsonl(results/'harness_rows.jsonl')
    variants = [v for v in MAIN+ABLATIONS if any(i['row']['variant'] == v for i in items)]
    cards = []
    for v in variants:
        card = scorecard([i['row'] for i in items if i['row']['variant'] == v])
        cards.append(dict(card, variant=v, label=LABELS[v]))
    write_csv(results/'scorecard_m3.csv', SCORE_COLUMNS, cards)
    write_csv(results/'scorecard_casos_m3.csv', CASE_COLUMNS, [case_row(i) for i in items])
    lines = ['| Sistema | Dim. 1 exactitud (0-1) | Dim. 2 juez (1-5, válidos) | Dim. 3 dominio | Latencia mediana (s) |',
             '|---|---:|---:|---:|---:|']
    for c in cards:
        lines.append(f"| {c['label']} | {fmt(c['dim1_accuracy'])} | {fmt(c['dim2_judge_mean'])} ({c['dim2_judge_valid']}/{c['cases']}) | "
                     f"{c['dim3_domain_passed']}/{c['cases']} ({fmt(c['dim3_domain_rate'])}) | {fmt(c['latency_median_seconds'], 2)} |")
    ragas_path = results/'ragas.jsonl'
    if ragas_path.exists():
        rag = read_jsonl(ragas_path)
        summaries = []
        for v in [v for v in MAIN+ABLATIONS if any(r['variant'] == v for r in rag)]:
            summaries.append(dict(summarize([r for r in rag if r['variant'] == v]), variant=v, label=LABELS[v]))
        cols = ['variant', 'label', 'cases'] + [x for m in APPLICABILITY for x in (m, m+'_n', m+'_na')] + \
               ['source_hit_rate', 'judge_calls', 'judge_parse_failures', 'ragas_version']
        write_csv(results/'ragas_m3.csv', cols, summaries)
        per_case = [{'variant': r['variant'], 'eval_id': r['eval_id'], 'kind': r['kind'],
                     **{m: r[m].get('value') for m in APPLICABILITY},
                     **{m+'_na': r[m].get('na') for m in APPLICABILITY},
                     'context_precision_simple': r['context_precision'].get('simple_fraction'),
                     'source_hit': r['source_hit'], 'judge_parse_failures': r['judge_parse_failures']}
                    for r in rag]
        write_csv(results/'ragas_casos_m3.csv', list(per_case[0]) if per_case else ['variant'], per_case)
        lines += ['', '| Sistema | Faithfulness | Answer relevancy | Context precision | Context recall | Fuente gold recuperada |',
                  '|---|---:|---:|---:|---:|---:|']
        for s in summaries:
            lines.append(f"| {s['label']} | " + ' | '.join(f"{fmt(s[m])} (n={s[m+'_n']})" for m in APPLICABILITY)
                         + f" | {fmt(s['source_hit_rate'])} |")
    (results/'tablas_m3.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('results', type=Path)
    print(build(parser.parse_args().results))
