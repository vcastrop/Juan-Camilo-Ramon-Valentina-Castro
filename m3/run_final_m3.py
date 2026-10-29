"""FINAL M3 evaluation on the frozen gold: 4 rows + 2 ablations, judge and RAGAS. Run on Colab T4.

Usage: python -u m3/run_final_m3.py --output NEW_DIRECTORY
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import statistics
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GOLD = ROOT/'eval/gold_v1/eval_set.json'
GOLD_SHA256 = 'bc4f8a7f74f2905576c34b559cc941df7d8d31d749227af78173136f8b361eca'
CORPUS_SHA256 = '7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505'
RAGAS_VARIANTS = ['rag_ingenuo', 'rag_avanzado', 'sistema_final']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gold():
    if sha(GOLD) != GOLD_SHA256:
        raise RuntimeError('Gold file changed; the frozen eval set must not be edited')
    return json.loads(GOLD.read_text(encoding='utf-8'))['cases']


def index_stats(docs, chunks):
    lengths = [len(c['text']) for c in chunks]
    per_doc = [sum(c['doc_id'] == d['doc_id'] for c in chunks) for d in docs]
    return {'documents': len(docs), 'chunks': len(chunks),
            'doc_chars_median': statistics.median(len(d['text']) for d in docs),
            'doc_chars_max': max(len(d['text']) for d in docs),
            'chunk_chars_median': statistics.median(lengths), 'chunk_chars_max': max(lengths),
            'chunks_per_doc_median': statistics.median(per_doc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-ablations', action='store_true')
    parser.add_argument('--skip-ragas', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output folder; previous evidence must be preserved')
    args.output.mkdir(parents=True)
    from run_integration_v5 import MODELS
    from sistemas_m3 import ABLATIONS, CONFIG, LABELS, MAIN
    meta = {'status': 'started', 'purpose': 'final_gold_evaluation_m3',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
            'models': MODELS, 'config': CONFIG, 'labels': LABELS}

    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    save()
    try:
        from sqlite_support import ensure_sqlite
        meta['sqlite'] = ensure_sqlite()
        import torch
        import numpy as np
        from huggingface_hub import snapshot_download
        from sentence_transformers import CrossEncoder
        from ingest import chunk_documents
        from rag_basic import DenseRetriever
        from response_v4 import TrackedGenerator
        from protocol_probe import ANSWER_V5, ROUTER_V5
        from judge import BASE_SYSTEM, IndependentJudge, RUBRIC_VERSION
        from harness_m3 import HARNESS_VERSION, RULES, harness
        from ragas_m3 import APPLICABILITY, RAGAS_VERSION, LabRagas
        from sistemas_m3 import construir
        import report_m3
        if not torch.cuda.is_available():
            raise RuntimeError('Enable a Colab T4 GPU')
        random.seed(CONFIG['seed']); np.random.seed(CONFIG['seed'])
        torch.manual_seed(CONFIG['seed']); torch.cuda.manual_seed_all(CONFIG['seed'])
        if sha(ROOT/'corpus/documents.jsonl') != CORPUS_SHA256:
            raise RuntimeError('Corpus changed after the gold was frozen')
        gold = load_gold()
        meta.update(gpu=torch.cuda.get_device_name(0),
                    packages={p: importlib.metadata.version(p) for p in
                              ['torch', 'numpy', 'transformers', 'sentence-transformers', 'chromadb',
                               'rank-bm25', 'pysqlite3-binary', 'huggingface-hub']},
                    source_hashes={p.name: sha(p) for p in sorted(ROOT.glob('*.py'))},
                    corpus_sha256=CORPUS_SHA256, gold_sha256=GOLD_SHA256, gold_cases=len(gold),
                    prompt_sha256=hashlib.sha256(ANSWER_V5.encode()).hexdigest(),
                    router_sha256=hashlib.sha256(ROUTER_V5.encode()).hexdigest(),
                    judge_system_sha256=hashlib.sha256(BASE_SYSTEM.encode()).hexdigest(),
                    harness_version=HARNESS_VERSION, harness_rules=RULES, judge_rubric_version=RUBRIC_VERSION,
                    judge_mitigate_verbosity=False, judge_model=MODELS['generator'],
                    judge_model_same_as_generator=True, ragas_version=RAGAS_VERSION,
                    ragas_applicability=APPLICABILITY, ragas_judge_model=MODELS['generator'],
                    ragas_embedding_model=MODELS['embedding'],
                    latency_policy=RULES['latency'])
        save()
        docs = [json.loads(l) for l in (ROOT/'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        chunks = chunk_documents(docs, CONFIG['chunk_chars'], CONFIG['overlap_chars'])
        (args.output/'chunks.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False)+'\n' for c in chunks), encoding='utf-8')
        meta['index'] = index_stats(docs, chunks)
        start = time.perf_counter()
        print('Building dense Chroma index from scratch...', flush=True)
        dense = DenseRetriever(chunks, *MODELS['embedding'], include_identity=True)
        meta['index']['index_seconds'] = time.perf_counter()-start
        print('Loading fixed-revision reranker...', flush=True)
        local = snapshot_download(MODELS['reranker'][0], revision=MODELS['reranker'][1],
                                  allow_patterns=['config.json', 'model.safetensors', 'pytorch_model.bin',
                                                  'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json',
                                                  'sentencepiece.bpe.model', 'vocab.*', 'merges.txt'])
        scorer = CrossEncoder(local, max_length=512, device='cpu')
        print('Loading generator...', flush=True)
        generator = TrackedGenerator(*MODELS['generator'], max_new_tokens=CONFIG['max_new_tokens'])
        meta['loading_total_seconds'] = time.perf_counter()-start
        save()
        systems = construir(dense, chunks, scorer, generator, docs)
        judge = IndependentJudge(generator, mitigate_verbosity=False)
        variants = MAIN + ([] if args.skip_ablations else ABLATIONS)
        records = {}
        with (args.output/'harness_rows.jsonl').open('w', encoding='utf-8') as out:
            def emit(item):
                out.write(json.dumps(item, ensure_ascii=False)+'\n'); out.flush()
            for name in variants:
                t0 = time.perf_counter()
                rows, card = harness(gold, systems[name], judge, dense.encoder, emit, name)
                records[name] = [r['record'] for r in rows]
                meta.setdefault('variant_wall_seconds', {})[name] = time.perf_counter()-t0
                meta.setdefault('scorecards', {})[name] = card
                print(json.dumps(dict(card, variant=name), ensure_ascii=False), flush=True)
                save()
        if not args.skip_ragas:
            ragas = LabRagas(generator, dense.encoder)
            t0 = time.perf_counter()
            with (args.output/'ragas.jsonl').open('w', encoding='utf-8') as out:
                for name in RAGAS_VARIANTS:
                    for case, record in zip(gold, records[name]):
                        print(f'RAGAS {name} {case["eval_id"]}', flush=True)
                        out.write(json.dumps(ragas.evaluate(case, dict(record, variant=name)), ensure_ascii=False)+'\n'); out.flush()
            meta['ragas_wall_seconds'] = time.perf_counter()-t0
        print(report_m3.build(args.output), flush=True)
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
