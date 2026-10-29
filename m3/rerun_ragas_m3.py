"""Recompute RAGAS 1.1 on the SAVED answers of a final run (no answer regeneration). Colab T4.

Usage: python -u m3/rerun_ragas_m3.py --run m3/results/final_m3 --output NEW_DIRECTORY
"""
import argparse
import csv
import hashlib
import json
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VARIANTS = ['rag_ingenuo', 'rag_avanzado', 'sistema_final']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output folder; previous evidence must be preserved')
    args.output.mkdir(parents=True)
    from run_integration_v5 import MODELS
    from run_final_m3 import load_gold
    from ragas_m3_v11 import APPLICABILITY, METRICS, RAGAS_VERSION, LabRagasV11, summarize
    from sistemas_m3 import LABELS, CONFIG
    source = args.run/'harness_rows.jsonl'
    meta = {'status': 'started', 'started_utc': datetime.now(timezone.utc).isoformat(),
            'ragas_version': RAGAS_VERSION, 'applicability': APPLICABILITY, 'judge_model': MODELS['generator'],
            'embedding_model': MODELS['embedding'], 'source_run': str(args.run),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'regenerated_answers': False}

    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    save()
    try:
        import torch
        import numpy as np
        from sentence_transformers import SentenceTransformer
        from response_v4 import TrackedGenerator
        if not torch.cuda.is_available():
            raise RuntimeError('Enable a Colab T4 GPU')
        random.seed(CONFIG['seed']); np.random.seed(CONFIG['seed']); torch.manual_seed(CONFIG['seed'])
        gold = {c['eval_id']: c for c in load_gold()}
        items = [json.loads(l) for l in source.read_text(encoding='utf-8').splitlines() if l.strip()]
        encoder = SentenceTransformer(*MODELS['embedding'][:1], revision=MODELS['embedding'][1], device='cpu')
        generator = TrackedGenerator(*MODELS['generator'], max_new_tokens=CONFIG['max_new_tokens'])
        ragas = LabRagasV11(generator, encoder)
        meta['gpu'] = torch.cuda.get_device_name(0)
        t0, results = time.perf_counter(), []
        with (args.output/'ragas_v1_1.jsonl').open('w', encoding='utf-8') as out:
            for item in items:
                variant = item['row']['variant']
                if variant not in VARIANTS:
                    continue
                print(f"RAGAS 1.1 {variant} {item['row']['eval_id']}", flush=True)
                result = ragas.evaluate(gold[item['row']['eval_id']], dict(item['record'], variant=variant))
                results.append(result)
                out.write(json.dumps(result, ensure_ascii=False)+'\n'); out.flush()
        meta['wall_seconds'] = time.perf_counter()-t0
        summaries = [dict(summarize([r for r in results if r['variant'] == v]), variant=v, label=LABELS[v]) for v in VARIANTS]
        cols = ['variant', 'label', 'cases'] + [x for m in METRICS for x in (m, m+'_n')] + ['judge_calls', 'judge_parse_failures', 'ragas_version']
        with (args.output/'ragas_m3_v1_1.csv').open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
            w.writeheader(); w.writerows(summaries)
        lines = ['| Sistema | Faithfulness | Answer relevancy | Context precision (lab) | Context recall (lab) | Context precision (rango) | Context recall (segmentos) |',
                 '|---|---:|---:|---:|---:|---:|---:|']
        for s in summaries:
            lines.append(f"| {s['label']} | " + ' | '.join('N/A' if s[m] is None else f"{s[m]:.3f} (n={s[m+'_n']})" for m in METRICS) + ' |')
        (args.output/'tablas_ragas_v1_1.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
        print('\n'.join(lines), flush=True)
        meta['status'] = 'completed'
    except Exception as exc:
        meta.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    main()
