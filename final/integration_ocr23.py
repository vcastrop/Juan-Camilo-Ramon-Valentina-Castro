"""Deployment factory with CPU adapter loading. OCR20 prediction logic is unchanged."""
from final.integration_ocr20 import RuntimeOCR,IntegratedOCRSystem,BoundOCR


def load_runtime():
    from final.service_environment import require_environment
    require_environment()
    from sqlite_support import ensure_sqlite
    ensure_sqlite()
    import random
    import numpy as np
    import torch
    from huggingface_hub import snapshot_download
    from sentence_transformers import CrossEncoder
    from rag_basic import DenseRetriever
    from ingest import chunk_documents
    from retrieval_advanced import HybridRetriever,RerankedRetriever
    from contract_tools import ContractTools
    from final.service_runtime import verify_assets
    from final.config import MODELS
    from final.adapters import AnswerAdapter,CompleteFieldRetriever
    from final.classifier_cpu23 import CPUClassifier
    from final.generators import NativeChatGenerator
    from final.ocr_candidate19 import OCRCandidate
    reader=OCRCandidate()
    docs=verify_assets()
    random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42)
    dense=DenseRetriever(chunk_documents(docs,220,30),*MODELS['embedding'],include_identity=True)
    local=snapshot_download(MODELS['reranker'][0],revision=MODELS['reranker'][1],allow_patterns=[
        'config.json','model.safetensors','pytorch_model.bin','tokenizer.json','tokenizer_config.json',
        'special_tokens_map.json','sentencepiece.bpe.model','vocab.*','merges.txt'])
    scorer=CrossEncoder(local,max_length=512,device='cpu')
    classifier=CPUClassifier()
    generator=NativeChatGenerator(*MODELS['generator'],precision='fp16',max_new_tokens=512)
    class Answer(AnswerAdapter):
        def __init__(self):
            self.generator=generator;self.tools=ContractTools(docs)
            self.retriever=CompleteFieldRetriever(RerankedRetriever(HybridRetriever(dense,list(dense.chunks.values())),scorer),docs)
    system=IntegratedOCRSystem(docs,Answer(),classifier,BoundOCR(reader))
    probe=dense.encoder.encode([dense.index_texts[0]],normalize_embeddings=True).tolist()
    return RuntimeOCR(system,dense,scorer,generator,classifier,reader,probe)
