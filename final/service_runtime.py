"""Real startup factory. No reference sets, stored answers, judge API or precision fallback."""
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.config import MODELS

CORPUS_SHA = '7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505'
ADAPTER_SHA = '869a45076bf2244917883970a00c966ba93c8b43a32fceb8c0a15b5d7efb387c'


def verify_assets(root=ROOT):
    root = Path(root)
    for name, sha in [('m3/corpus/documents.jsonl', CORPUS_SHA),
                      ('model/contractrisk_robertalex_lora_adapter.zip', ADAPTER_SHA)]:
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != sha:
            raise ValueError('Runtime source asset differs: '+name)
    docs = [json.loads(s) for s in (root/'m3/corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
    if len(docs) != 24 or len({d['doc_id'] for d in docs}) != 24:
        raise ValueError('Expected the reviewed 24-record source corpus')
    return docs


class Runtime:
    def __init__(self, system, dense, scorer, generator, vision, classifier, probe):
        self.system, self.dense, self.scorer = system, dense, scorer
        self.generator, self.vision, self.classifier = generator, vision, classifier
        self.probe = probe

    def model_state(self):
        return {'generator': hasattr(self.generator, 'model'), 'vision': hasattr(self.vision, 'model'),
                'classifier': hasattr(self.classifier, 'model'), 'embedding': hasattr(self.dense, 'encoder'),
                'reranker': self.scorer is not None}

    def index_probe(self):
        if self.dense.collection.count() != len(self.dense.chunks): return False
        result = self.dense.collection.query(query_embeddings=self.probe, n_results=1)
        return bool(result.get('ids') and result['ids'][0] and result['ids'][0][0] in self.dense.chunks)

    def predict(self, question, image=None, mode='qa', description=None):
        return self.system.predict(question, image=image, mode=mode, description=description)


def load_runtime():
    # Called once at Space startup AFTER importing spaces. ZeroGPU supplies CUDA
    # emulation during startup. Ordinary Colab requires a real GPU here.
    from final.service_environment import require_environment
    require_environment()
    from sqlite_support import ensure_sqlite
    ensure_sqlite()
    import numpy as np
    import torch
    from huggingface_hub import snapshot_download
    from sentence_transformers import CrossEncoder
    from rag_basic import DenseRetriever
    from ingest import chunk_documents
    from retrieval_advanced import HybridRetriever, RerankedRetriever
    from contract_tools import ContractTools
    from final.adapters import AnswerAdapter, CompleteFieldRetriever, Vision, Classifier
    from final.generators import NativeChatGenerator
    from final.integration import IntegratedSystem
    docs = verify_assets()
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    dense = DenseRetriever(chunk_documents(docs, 220, 30), *MODELS['embedding'], include_identity=True)
    local = snapshot_download(MODELS['reranker'][0], revision=MODELS['reranker'][1], allow_patterns=[
        'config.json', 'model.safetensors', 'pytorch_model.bin', 'tokenizer.json', 'tokenizer_config.json',
        'special_tokens_map.json', 'sentencepiece.bpe.model', 'vocab.*', 'merges.txt'])
    scorer = CrossEncoder(local, max_length=512, device='cpu')
    classifier = Classifier()
    generator = NativeChatGenerator(*MODELS['generator'], precision='fp16', max_new_tokens=512)
    vision = Vision()

    class PublicAnswer(AnswerAdapter):
        def __init__(self):
            self.generator = generator
            self.tools = ContractTools(docs)
            self.retriever = CompleteFieldRetriever(
                RerankedRetriever(HybridRetriever(dense, list(dense.chunks.values())), scorer), docs)

    system = IntegratedSystem(docs, PublicAnswer(), classifier=classifier, vision=vision)
    # A cached source-vector probe: no real user question, generation or GPU inference.
    probe = dense.encoder.encode([dense.index_texts[0]], normalize_embeddings=True).tolist()
    return Runtime(system, dense, scorer, generator, vision, classifier, probe)
