"""Colab T4: re-evaluate frozen answers only, without rerunning retrieval/generation."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import traceback
from pathlib import Path
from datetime import datetime, timezone
from run_final_m3 import load_gold, RAGAS_VARIANTS
from run_integration_v5 import MODELS
from ragas_audit_m3 import AuditedRagas, VERSION
from ragas_m3 import summarize, APPLICABILITY

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = ROOT/'results/final_m3/harness_rows.jsonl'
    meta = {'status': 'started', 'purpose': 'post_hoc_ragas_on_frozen_answers', 'seed': 42,
            'version': VERSION, 'models': MODELS, 'python': platform.python_version(),
            'started_utc': datetime.now(timezone.utc).isoformat(),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'code_sha256': {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                            for n in ['ragas_audit_m3.py', 'ragas_m3.py', 'run_ragas_audit_m3.py']},
            'applicability': APPLICABILITY,
            'limitations': ['same Qwen model family as generator, not an independent human reference',
                            'post-hoc evaluator correction; gold already inspected',
                            'abstention excluded by legacy policy, not because it cannot contain factual claims',
                            'rank-aware context precision and per-statement recall adapt rather than exactly reproduce S10']}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        import numpy as np
        import torch
        from sentence_transformers import SentenceTransformer
        from response_v4 import TrackedGenerator
        if not torch.cuda.is_available():
            raise RuntimeError('Activa una GPU T4 en Colab')
        random.seed(42); np.random.seed(42); torch.manual_seed(42); torch.cuda.manual_seed_all(42)
        meta.update(gpu=torch.cuda.get_device_name(0), packages={p: importlib.metadata.version(p)
                    for p in ['torch', 'transformers', 'numpy', 'sentence-transformers']})
        gold = {c['eval_id']: c for c in load_gold()}
        items = [json.loads(s) for s in source.read_text(encoding='utf-8').splitlines() if s.strip()]
        selected = [i for i in items if i['row']['variant'] in RAGAS_VARIANTS]
        expected = {(v, e) for v in RAGAS_VARIANTS for e in gold}
        actual = [(i['row']['variant'], i['row']['eval_id']) for i in selected]
        if len(actual) != len(expected) or set(actual) != expected:
            raise ValueError('Duplicate or missing frozen answers')
        encoder = SentenceTransformer(MODELS['embedding'][0], revision=MODELS['embedding'][1], device='cpu')
        generator = TrackedGenerator(*MODELS['generator'], max_new_tokens=512)
        evaluator = AuditedRagas(generator, encoder)
        results = []
        with (args.output/'ragas.jsonl').open('w', encoding='utf-8') as out:
            for i, item in enumerate(selected, 1):
                case = gold[item['row']['eval_id']]
                record = dict(item['record'], variant=item['row']['variant'])
                if record['question'] != case['input']:
                    raise ValueError('Frozen question mismatch')
                print(f"RAGAS audit {i}/{len(selected)}: {record['variant']} {case['eval_id']}", flush=True)
                result = evaluator.evaluate(case, record)
                results.append(result)
                out.write(json.dumps(result, ensure_ascii=False)+'\n'); out.flush()
        meta['summaries'] = {v: dict(summarize([r for r in results if r['variant'] == v]), ragas_version=VERSION)
                             for v in RAGAS_VARIANTS}
        meta['status'] = 'completed'
        print(json.dumps(meta['summaries'], indent=2), flush=True)
    except Exception as exc:
        meta.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    main()
