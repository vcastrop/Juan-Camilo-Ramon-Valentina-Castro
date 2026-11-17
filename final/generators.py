"""Pinned causal model loader, real CUDA only. No automatic precision fallback."""
import gc
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'m3'))
from response_v4 import TrackedGenerator


def precision_settings(precision):
    if precision not in ['fp16','nf4']:
        raise ValueError('Precision must be fp16 or nf4')
    return {'precision':precision,'compute_dtype':'float16','double_quantization':precision=='nf4',
            'quantization_type':'nf4' if precision=='nf4' else None,'cpu_offload':False}


class CausalGenerator(TrackedGenerator):
    def __init__(self,name,revision,precision='fp16',max_new_tokens=320):
        self.load_settings=precision_settings(precision)
        if type(max_new_tokens) is not int or max_new_tokens<=0:
            raise ValueError('Invalid token limit')
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
        if not torch.cuda.is_available():raise RuntimeError('Enable Colab T4')
        self.torch=torch;self.max_new_tokens=max_new_tokens
        self.tokenizer=AutoTokenizer.from_pretrained(name,revision=revision)
        kwargs={'revision':revision,'torch_dtype':torch.float16,'device_map':{'':0}}
        if precision=='nf4':
            kwargs['quantization_config']=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',
                bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
        self.model=AutoModelForCausalLM.from_pretrained(name,**kwargs).eval()
        self.quantized_linear_layers=0
        if precision=='nf4':
            from bitsandbytes.nn import Linear4bit
            self.quantized_linear_layers=sum(isinstance(m,Linear4bit) for m in self.model.modules())
            if not getattr(self.model,'is_loaded_in_4bit',False) or not self.quantized_linear_layers:
                raise RuntimeError('Requested NF4 did not load genuine 4-bit layers')
        if any(p.device.type!='cuda' for p in self.model.parameters()):
            raise RuntimeError('Unexpected model CPU offload; comparison configuration changed')
        self.load_settings.update(name=name,revision=revision,quantized_linear_layers=self.quantized_linear_layers,
                                  quantization_verified=precision=='nf4' and self.quantized_linear_layers>0)

    def close(self):
        if hasattr(self,'model'):del self.model
        gc.collect();self.torch.cuda.empty_cache()
