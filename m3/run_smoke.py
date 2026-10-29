"""Real-model development smoke test, NOT final evaluation or a scorecard."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ingest import chunk_documents
from rag_basic import BasicRAG, DenseRetriever, LocalGenerator

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output directory must not exist; preserve every run')
    import torch
    import numpy as np
    from huggingface_hub import HfApi
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    if not torch.cuda.is_available():
        raise RuntimeError('Enable a GPU before this test')
    args.output.mkdir(parents=True)
    metadata = {'status': 'started', 'purpose': 'development_smoke_not_final_evaluation',
                'seed': 42, 'started_utc': datetime.now(timezone.utc).isoformat(),
                'python': platform.python_version(), 'gpu': torch.cuda.get_device_name(0),
                'packages': {p: importlib.metadata.version(p) for p in ['torch', 'transformers', 'sentence-transformers', 'chromadb', 'numpy']}}
    try:
        metadata['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        metadata['git_commit'] = None
    def save():
        (args.output / 'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        names = {'embedding': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                 'generator': 'Qwen/Qwen2.5-1.5B-Instruct'}
        revisions = {k: HfApi().model_info(v).sha for k, v in names.items()}
        metadata.update(models=names, revisions=revisions)
        corpus = ROOT / 'corpus/documents.jsonl'
        metadata['corpus_sha256'] = hashlib.sha256(corpus.read_bytes()).hexdigest()
        docs = [json.loads(l) for l in corpus.read_text(encoding='utf-8').splitlines()]
        # Shorter than the exploratory 800-char chunks, to respect MiniLM's 128-token limit.
        chunks = chunk_documents(docs, max_chars=280, overlap_chars=40)
        metadata.update(chunk_chars=280, overlap_chars=40, chunk_count=len(chunks), top_k=3)
        save()
        print('Building dense index...', flush=True)
        retriever = DenseRetriever(chunks, names['embedding'], revisions['embedding'])
        print('Loading generator...', flush=True)
        generator = LocalGenerator(names['generator'], revisions['generator'])
        rag = BasicRAG(retriever, generator)
        cases = json.loads((ROOT / 'eval/development_questions.json').read_text(encoding='utf-8'))['cases']
        with (args.output / 'predictions.jsonl').open('w', encoding='utf-8') as handle:
            for i, case in enumerate(cases):
                print(f'Development question {i+1}/{len(cases)}', flush=True)
                result = rag.predict(case['input'])
                # Reference added after inference exclusively for human diagnosis.
                result['reference_for_review_only'] = case['expected']
                handle.write(json.dumps(result, ensure_ascii=False)+'\n')
                handle.flush()
        metadata['status'] = 'completed'
    except Exception as exc:
        metadata.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
