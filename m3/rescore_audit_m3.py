"""Re-score saved predictions, NEVER regenerate answers or overwrite original evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from audit_rules_m3 import VERSION, score_case
from harness_m3 import scorecard
from run_final_m3 import load_gold

ROOT = Path(__file__).resolve().parent


def rescore(source, destination):
    items = [json.loads(s) for s in source.read_text(encoding='utf-8').splitlines() if s.strip()]
    gold = {c['eval_id']: c for c in load_gold()}
    seen = set()
    changes, revised = [], []
    for item in items:
        old = item['row']
        key = (old['variant'], old['eval_id'])
        if key in seen:
            raise ValueError(f'Duplicate prediction: {key}')
        seen.add(key)
        case = gold[old['eval_id']]
        if item['record'].get('question') != case['input']:
            raise ValueError(f'Question mismatch: {key}')
        new = dict(old, **score_case(case, item['record']))
        new['m2_compatible_pass'] = bool(new['accuracy'] == 1 and new.get('judge_score') is not None
                                         and new['judge_score'] >= 4)
        delta = {k: {'original': old.get(k), 'audit': v} for k, v in new.items() if old.get(k) != v}
        if delta:
            changes.append({'variant': key[0], 'eval_id': key[1], 'changes': delta})
        revised.append(dict(item, row=new))
    variants = sorted({v for v, _ in seen})
    for variant in variants:
        if {e for v, e in seen if v == variant} != set(gold):
            raise ValueError(f'Incomplete gold coverage: {variant}')
    cards = {v: dict(scorecard([i['row'] for i in revised if i['row']['variant'] == v]),
                     harness_version=VERSION) for v in variants}
    destination.mkdir(parents=True, exist_ok=False)
    (destination/'harness_rows.jsonl').write_text(''.join(json.dumps(i, ensure_ascii=False)+'\n'
                                                        for i in revised), encoding='utf-8')
    manifest = {'version': VERSION, 'purpose': 'post_hoc_rescore_not_new_inference',
                'created_utc': datetime.now(timezone.utc).isoformat(),
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source': 'm3/results/final_m3/harness_rows.jsonl',
                'code_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                                for name in ['audit_rules_m3.py', 'rescore_audit_m3.py', 'harness_m3.py']},
                'responses_judge_and_latency': 'unchanged from original run',
                'ragas': 'not recalculated; requires fresh judge calls after statement splitting fix',
                'scorecards': cards, 'changed_cases': changes}
    (destination/'audit.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# Recálculo posterior de reglas deterministas', '',
             'No es una nueva corrida del modelo. Respuestas, juez y latencias son los originales.',
             'La cobertura léxica no demuestra verdad semántica. Se aplican las mismas reglas a las seis variantes.', '',
             '| Variante | Cobertura de hechos | Juez original | Dominio auditado |',
             '|---|---:|---:|---:|']
    for v, c in cards.items():
        lines.append(f"| {v} | {c['dim1_accuracy']:.3f} | {c['dim2_judge_mean']:.3f} | {c['dim3_domain_passed']}/{c['cases']} |")
    lines += ['', f'Casos con cambios de evaluación: {len(changes)}. Detalle: `audit.json`.',
              'RAGAS no se recalculó en este paso. No mezclar su versión original con una nueva sin identificarla.']
    (destination/'RESUMEN.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'results/final_m3/harness_rows.jsonl')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = rescore(args.source, args.output)
    print(json.dumps({'version': VERSION, 'changed_cases': result['changed_cases']}, ensure_ascii=False, indent=2))
