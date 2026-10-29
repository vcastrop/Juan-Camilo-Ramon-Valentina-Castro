"""Three retrieval variants on development queries only. Not the final M3 harness."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output directory; preserve previous runs')
    args.output.mkdir(parents=True)
    meta = {'status': 'started', 'purpose': 'development_v2_not_final_scorecard',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(), 'seed': 42}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        from sqlite_support import ensure_sqlite
        meta['sqlite'] = ensure_sqlite()
        import torch
        import numpy as np
        from huggingface_hub import HfApi, snapshot_download
        from sentence_transformers import CrossEncoder
        from ingest import chunk_documents
        from rag_basic import BasicRAG, DenseRetriever, LocalGenerator, SYSTEM_V2
        from retrieval_advanced import HybridRetriever, RerankedRetriever
        random.seed(42); np.random.seed(42); torch.manual_seed(42); torch.cuda.manual_seed_all(42)
        if not torch.cuda.is_available():
            raise RuntimeError('Enable Colab GPU T4')
        meta['gpu'] = torch.cuda.get_device_name(0)
        meta['packages'] = {p: importlib.metadata.version(p) for p in ['torch','numpy','transformers','sentence-transformers','chromadb','rank-bm25','pysqlite3-binary']}
        names = {'embedding':'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                 'generator':'Qwen/Qwen2.5-1.5B-Instruct', 'reranker':'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'}
        revisions = {'embedding':'e8f8c211226b894fcb81acc59f3b34ba3efd5f42',
                     'generator':'989aa7980e4cf806f80c7fef2b1adb7bc71aa306',
                     'reranker':HfApi().model_info(names['reranker']).sha}
        corpus = ROOT/'corpus/documents.jsonl'
        meta.update(models=names, revisions=revisions, corpus_sha256=hashlib.sha256(corpus.read_bytes()).hexdigest(),
                    prompt_version='v2', prompt_sha256=hashlib.sha256(SYSTEM_V2.encode()).hexdigest(),
                    chunk_chars=220, overlap_chars=30, identity_in_embeddings=True, top_k=3, candidate_count=12)
        meta['source_hashes'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}
        save()
        docs = [json.loads(s) for s in corpus.read_text(encoding='utf-8').splitlines()]
        chunks = chunk_documents(docs, 220, 30)
        meta['chunk_count'] = len(chunks)
        (args.output/'chunks.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chunks),encoding='utf-8')
        print('Building dense index with contract identity...', flush=True)
        dense = DenseRetriever(chunks, names['embedding'], revisions['embedding'], include_identity=True)
        hybrid = HybridRetriever(dense, chunks)
        print('Loading reranker...', flush=True)
        local = snapshot_download(names['reranker'], revision=revisions['reranker'],
                                  allow_patterns=['config.json','model.safetensors','pytorch_model.bin',
                                                  'tokenizer.json','tokenizer_config.json','special_tokens_map.json',
                                                  'sentencepiece.bpe.model','vocab.*','merges.txt'])
        scorer = CrossEncoder(local, max_length=512, device='cpu')
        reranked = RerankedRetriever(hybrid, scorer)
        print('Loading generator...', flush=True)
        generator = LocalGenerator(names['generator'], revisions['generator'])
        variants = {'dense_v2':dense, 'hybrid_idfilter_v2':hybrid, 'hybrid_idfilter_rerank_v2':reranked}
        cases = json.loads((ROOT/'eval/development_questions.json').read_text(encoding='utf-8'))['cases']
        # Additional synthetic protocol probe: deliberately empty evidence, not a gold case.
        cases = cases + [{'input':'Según las fuentes proporcionadas, ¿cuál es la fecha del acta de liquidación?', 'empty_context_probe':True}]
        with (args.output/'predictions.jsonl').open('w',encoding='utf-8') as out:
            for name, retriever in variants.items():
                rag = BasicRAG(retriever, generator, system_prompt=SYSTEM_V2)
                for i, case in enumerate(cases):
                    print(f'{name}: {i+1}/{len(cases)}', flush=True)
                    result = rag.predict(case['input'], retrieve=not case.get('empty_context_probe', False))
                    result.update(variant=name, development_index=i, empty_context_probe=case.get('empty_context_probe', False))
                    result['reference_for_review_only'] = case.get('expected')
                    result['expected_source_ids_for_review_only'] = case.get('source_ids', [])
                    out.write(json.dumps(result,ensure_ascii=False)+'\n'); out.flush()
        meta['status'] = 'completed'
    except Exception as exc:
        meta.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
