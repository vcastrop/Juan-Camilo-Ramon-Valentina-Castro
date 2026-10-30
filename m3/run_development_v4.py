"""Development v4, not final evaluation. Run with --output NEW_DIRECTORY on T4."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = {
    'embedding': ('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', 'e8f8c211226b894fcb81acc59f3b34ba3efd5f42'),
    'generator': ('Qwen/Qwen2.5-1.5B-Instruct', '989aa7980e4cf806f80c7fef2b1adb7bc71aa306'),
    'reranker': ('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1', '1427fd652930e4ba29e8149678df786c240d8825'),
}


def development_cases():
    cases = json.loads((ROOT/'eval/development_questions.json').read_text(encoding='utf-8'))['cases']
    # Reuse DEVELOPMENT document IDs, never final QA questions/references.
    result = [{'input': c['input'], 'expected_for_review': c['expected'],
               'kind': 'modality', 'tool_expected_for_review': False} for c in cases]
    for a, b in [('1180445', '1637043'), ('3156756', '5484069')]:
        result.append({'input': f'¿Cuál es la diferencia absoluta entre los valores registrados de CO1.PCCNTR.{a} y CO1.PCCNTR.{b}? Muestra la operación y cita ambas fuentes.',
                       'kind': 'calculation', 'tool_expected_for_review': True})
    result.extend([
        {'input': '¿Cuál es el texto literal de la cláusula de multas de CO1.PCCNTR.1180445?',
         'kind': 'absent_document', 'tool_expected_for_review': False},
        {'input': '¿Qué concluyó la auditoría de ejecución física de CO1.PCCNTR.1637043?',
         'kind': 'absent_document', 'tool_expected_for_review': False},
    ])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output folder; previous evidence must be preserved')
    args.output.mkdir(parents=True)
    meta = {'status': 'started', 'purpose': 'development_v4_not_final_scorecard',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'seed': 42,
            'python': platform.python_version(), 'models': MODELS}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8')
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
        from response_v4 import TrackedGenerator, CompactRAG, SYSTEM_V4
        from retrieval_advanced import HybridRetriever, RerankedRetriever
        from agent_v4 import CompactAgent, CONTROLLER_V4
        from contract_tools import ContractTools
        if not torch.cuda.is_available():
            raise RuntimeError('Enable a Colab T4 GPU')
        random.seed(42); np.random.seed(42); torch.manual_seed(42); torch.cuda.manual_seed_all(42)
        meta.update(gpu=torch.cuda.get_device_name(0),
                    packages={p: importlib.metadata.version(p) for p in
                              ['torch','numpy','transformers','sentence-transformers','chromadb','rank-bm25','pysqlite3-binary']},
                    source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},
                    corpus_sha256=hashlib.sha256((ROOT/'corpus/documents.jsonl').read_bytes()).hexdigest(),
                    prompt_version='v4_candidate', prompt_sha256=hashlib.sha256(SYSTEM_V4.encode()).hexdigest(),
                    controller_sha256=hashlib.sha256(CONTROLLER_V4.encode()).hexdigest(),
                    chunk_chars=220, overlap_chars=30, identity_in_embeddings=True,
                    top_k=3, candidate_count=12, max_controller_steps=3, max_new_tokens=512,
                    latency_policy='wall-clock per predict; excludes loading and evaluation; no discarded warmup',
                    evaluation_status='not_run; manual development inspection only')
        docs = [json.loads(l) for l in (ROOT/'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        chunks = chunk_documents(docs, 220, 30)
        (args.output/'chunks.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False)+'\n' for c in chunks), encoding='utf-8')
        load_start = time.perf_counter()
        print('Building dense index...', flush=True)
        dense = DenseRetriever(chunks, *MODELS['embedding'], include_identity=True)
        meta['index_seconds'] = time.perf_counter()-load_start
        hybrid = HybridRetriever(dense, chunks)
        print('Loading fixed-revision reranker...', flush=True)
        local = snapshot_download(MODELS['reranker'][0], revision=MODELS['reranker'][1],
                                  allow_patterns=['config.json','model.safetensors','pytorch_model.bin',
                                                  'tokenizer.json','tokenizer_config.json','special_tokens_map.json',
                                                  'sentencepiece.bpe.model','vocab.*','merges.txt'])
        advanced = RerankedRetriever(hybrid, CrossEncoder(local, max_length=512, device='cpu'))
        print('Loading generator...', flush=True)
        generator = TrackedGenerator(*MODELS['generator'], max_new_tokens=512)
        meta.update(chunk_count=len(chunks), loading_total_seconds=time.perf_counter()-load_start)
        tools = ContractTools(docs)
        systems = {
            'control_no_rag_v4': CompactRAG(dense, generator),
            'dense_v4': CompactRAG(dense, generator),
            'advanced_v4': CompactRAG(advanced, generator),
            'agent_v4': CompactAgent(advanced, generator, tools),
        }
        cases = development_cases()
        meta['case_count'] = len(cases)
        meta['case_sha256'] = hashlib.sha256(json.dumps(cases, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        save()
        with (args.output/'predictions.jsonl').open('w', encoding='utf-8') as out:
            for name, system in systems.items():
                for i, case in enumerate(cases):
                    print(f'{name}: {i+1}/{len(cases)}', flush=True)
                    # Only question reaches the system, never development expected values.
                    result = system.predict(case['input'], retrieve=False) if name == 'control_no_rag_v4' else system.predict(case['input'])
                    result.update(variant=name, development_index=i, review_only=case)
                    out.write(json.dumps(result, ensure_ascii=False)+'\n'); out.flush()
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
