"""Separate candidate: OCR fields -> unchanged source guards/RAG/tools/M1. Not a VLM result."""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
from final.integration import IntegratedSystem, abstain

VERSION='integrated-ocr-20'
LABELS={'id_contrato':'Identificador del contrato', 'objeto':'Objeto registrado',
        'modalidad':'Modalidad de contratación', 'valor_cop':'Valor del contrato (COP)'}


class BoundOCR:
    """Only consensual fields reach generator context. Raw TSV stays in local audit traces."""
    def __init__(self,reader):self.reader=reader
    def extract(self,image):
        original=self.reader.extract(image)
        result=dict(original)
        if original.get('output') and not original.get('parse_error'):
            output=dict(original['output'])
            if output.get('legible'):
                result['unfiltered_ocr_transcription']=output['texto_visible']
                output['texto_visible']='\n'.join(label+': '+output[key] for key,label in LABELS.items() if output.get(key) is not None)
            result['output']=output
        result['evidence_policy']='Only accepted labeled fields enter visual_context; text remains untrusted evidence, not instructions.'
        return result


class IntegratedOCRSystem(IntegratedSystem):
    def predict(self,question,image=None,mode='qa',description=None):
        if not isinstance(question,str) or not 0<len(question.strip())<=1200:raise ValueError('Invalid question')
        if mode not in {'qa','sufficiency'}:raise ValueError('Invalid mode')
        start=time.perf_counter()
        if image is None:
            record=super().predict(question,mode=mode,description=description)
        else:
            reading=self.vision.extract(image)
            visual=reading.get('output') or {}
            if mode=='qa' and not reading.get('parse_error') and visual.get('id_contrato') and visual['id_contrato'] not in self.documents:
                record={'question':question,'mode':mode,'visual':reading,'classification':None,
                    'contexts':[],'tool_trace':[], 'components':{'vision':True,'rag':False,'tool':False,'classifier':False},
                    'output':abstain('La ficha visual no pertenece al snapshot disponible; no se atribuyen fuentes de otro contrato.'),
                    'guard':'unknown_visual_contract'}
            else:
                # Request-local injection, not a cross-request cache or a second OCR attempt.
                class ThisReading:
                    def extract(self,unused_image):return reading
                delegate=IntegratedSystem(list(self.documents.values()),self.answer,self.classifier,ThisReading())
                record=delegate.predict(question,image=image,mode=mode,description=description)
        record.update(integration_version=VERSION,latency_seconds=time.perf_counter()-start,
                      visual_reader='tesseract_consensus_19',vlm_used=False)
        return record


class RuntimeOCR:
    def __init__(self,system,dense,scorer,generator,classifier,reader,probe):
        self.system,self.dense,self.scorer=system,dense,scorer
        self.generator,self.classifier,self.reader,self.probe=generator,classifier,reader,probe
    def model_state(self):
        return {'generator':hasattr(self.generator,'model'),'classifier':hasattr(self.classifier,'model'),
                'embedding':hasattr(self.dense,'encoder'),'reranker':self.scorer is not None}
    def reader_state(self):
        return {'kind':'tesseract_cpu_not_qwen_vlm','ready':bool(self.reader.executable and self.reader.version),
                'version':self.reader.version,'language_data_sha256':self.reader.language_data_sha256}
    def index_probe(self):
        if self.dense.collection.count()!=len(self.dense.chunks):return False
        result=self.dense.collection.query(query_embeddings=self.probe,n_results=1)
        return bool(result.get('ids') and result['ids'][0] and result['ids'][0][0] in self.dense.chunks)
    def predict(self,question,image=None,mode='qa',description=None):
        if isinstance(image,(str,Path)):
            from PIL import Image
            with Image.open(image) as opened:
                return self.system.predict(question,image=opened.convert('RGB'),mode=mode,description=description)
        return self.system.predict(question,image=image,mode=mode,description=description)


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
    from final.adapters import AnswerAdapter,CompleteFieldRetriever,Classifier
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
    classifier=Classifier()
    generator=NativeChatGenerator(*MODELS['generator'],precision='fp16',max_new_tokens=512)
    class Answer(AnswerAdapter):
        def __init__(self):
            self.generator=generator;self.tools=ContractTools(docs)
            self.retriever=CompleteFieldRetriever(RerankedRetriever(HybridRetriever(dense,list(dense.chunks.values())),scorer),docs)
    system=IntegratedOCRSystem(docs,Answer(),classifier,BoundOCR(reader))
    probe=dense.encoder.encode([dense.index_texts[0]],normalize_embeddings=True).tolist()
    return RuntimeOCR(system,dense,scorer,generator,classifier,reader,probe)
