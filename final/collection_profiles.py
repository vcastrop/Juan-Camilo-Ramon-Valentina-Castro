"""Real generation-only profiles. Historical modules remain unchanged."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
from final.config import MODELS

PROFILES=['qa_no_rag_fp16','m3_text_fp16','integrated_fp16','integrated_nf4','integrated_no_tool_fp16']
SETTINGS={'version':'common-collection-1.0.1-callable-fix','seed':42,'max_new_tokens':512,'do_sample':False,
    'chunk_chars':220,'overlap_chars':30,'identity_in_embeddings':True,'top_k':3,
    'profile_order':PROFILES,'repetitions':1,'judge_used':False,'semantic_protocol_frozen':False,
    'quantization':{'type':'nf4','double_quantization':True,'compute_dtype':'float16','bitsandbytes':'0.50.2'},
    'timing':'synchronized wall time including image file loading, retrieval and generation; excludes model/index loading and warmups',
    'memory':'per-case peak CUDA allocated/reserved of whole process; CPU embedding and reranker; no classifier in QA benchmark',
    'baseline_images':'explicit unsupported-image abstention, counted in all 22 rows; no gold transcription',
    'warmups':'fixed generic text question and rendered fictional image outside eval inputs; excluded; no response cache',
    'limitations':'One ordered pass, no counterbalancing; p95 is descriptive. QA no-RAG is an adaptation, not M2 classification. M3 uses legacy chat encoding; new visual pair uses native encoding. No efficiency acceptance before semantic evaluation.'}


class PathSystem:
    def __init__(self,system,vision_enabled):self.system=system;self.vision_enabled=vision_enabled
    def predict(self,question,image=None):
        if image is not None and not self.vision_enabled:
            from final.integration import abstain
            return {'question':question,'contexts':[],'tool_trace':[],'guard':'unsupported_image',
                    'output':abstain('Esta línea base no admite imágenes; no se le proporcionó una transcripción.'),
                    'components':{'rag':False,'vision':False,'tool':False}}
        if image is None:return self.system.predict(question)
        from PIL import Image
        with Image.open(image) as opened:
            return self.system.predict(question,image=opened.convert('RGB'))


class HistoricalCallable:
    """M3 construir returns question -> record functions, not objects with predict."""
    def __init__(self,callback):
        if not callable(callback):raise TypeError('M3 variant must be callable')
        self.callback=callback
    def predict(self,question):return self.callback(question)


def build_profile(name,documents,dense,scorer):
    if name not in PROFILES:raise ValueError('Unknown comparison profile')
    from final.generators import CausalGenerator,NativeChatGenerator
    from final.adapters import Vision,AnswerAdapter,CompleteFieldRetriever
    from final.integration import IntegratedSystem
    from retrieval_advanced import HybridRetriever,RerankedRetriever
    from contract_tools import ContractTools
    generator=vision=None
    try:
        visual=name.startswith('integrated_')
        loader=NativeChatGenerator if visual else CausalGenerator
        generator=loader(*MODELS['generator'],precision='nf4' if name=='integrated_nf4' else 'fp16',max_new_tokens=512)
        if not visual:
            from sistemas_m3 import construir
            historical=construir(dense,list(dense.chunks.values()),scorer,generator,documents)
            # M3's sin_rag wrapper already passes retrieve=False internally.
            key='sin_rag' if name=='qa_no_rag_fp16' else 'sistema_final'
            system=HistoricalCallable(historical[key])
        else:
            class InjectedAnswer(AnswerAdapter):
                def __init__(self):
                    self.generator=generator;self.tools=ContractTools(documents)
                    self.retriever=CompleteFieldRetriever(RerankedRetriever(HybridRetriever(dense,list(dense.chunks.values())),scorer),documents)
                def __call__(self,question,visual_context=None):
                    if name!='integrated_no_tool_fp16':return super().__call__(question,visual_context)
                    from systems_v5 import CandidateRAG
                    from final.integration import contract_ids
                    base=self.retriever
                    class WithImage:
                        def search(self,q,k):
                            extra=visual_context['doc_id'] if visual_context and not contract_ids(q) else ''
                            return ([visual_context] if visual_context else [])+base.search(q+' '+extra,k)
                    result=CandidateRAG(WithImage(),generator).predict(question)
                    result.update(tool_calls=0,tool_trace=[],tool_policy='ablation_disabled')
                    return result
            vision=Vision();system=IntegratedSystem(documents,InjectedAnswer(),vision=vision)
        return PathSystem(system,visual),generator,vision
    except Exception:
        if vision is not None:vision.close()
        if generator is not None:generator.close()
        raise


def warmup(system,folder):
    """Not an evaluation input; never look up references or prior model outputs."""
    from PIL import Image,ImageDraw
    path=Path(folder)/'warmup_synthetic.png'
    image=Image.new('RGB',(600,220),'white');draw=ImageDraw.Draw(image)
    draw.text((20,20),'SYNTHETIC WARMUP - NOT A REAL CONTRACT\nContract: CO1.PCCNTR.999000777\nValue COP: 17000',fill='black')
    image.save(path)
    return [system.predict('¿Qué información expresa el campo Modalidad de contratación en estas fuentes?'),
            system.predict('¿Qué valor aparece en la imagen?',image=path)]
