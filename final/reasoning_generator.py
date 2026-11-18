"""Qwen3 native reasoning-mode generation; public final verdict only, no private thinking text."""
import hashlib
import json
from final.generators import CausalGenerator


def extract_final_ids(ids,close_id):
    if ids.count(close_id)!=1:
        return None,{'thinking_closed':False,'generated_ids_sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest()}
    index=ids.index(close_id)+1
    thinking=ids[:index]
    return ids[index:],{'thinking_closed':True,'thinking_tokens':len(thinking),
                       'thinking_ids_sha256':hashlib.sha256(json.dumps(thinking).encode()).hexdigest(),
                       'generated_ids_sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest()}


def encode_reasoning_chat(tokenizer,system,user,return_tensors=None):
    messages=[{'role':'system','content':system},{'role':'user','content':user}]
    kwargs={'tokenize':False,'add_generation_prompt':True,'enable_thinking':True}
    text=tokenizer.apply_chat_template(messages,**kwargs)
    encoded=tokenizer(text,add_special_tokens=False,**({'return_tensors':return_tensors} if return_tensors else {}))
    ids=encoded['input_ids']
    if hasattr(ids,'tolist'):ids=ids.tolist()
    if len(ids)==1 and isinstance(ids[0],list):ids=ids[0]
    native=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=True)
    if ids!=native:raise ValueError('Reasoning chat differs from native tokenization')
    return encoded,{'native_equivalent':True,'enable_thinking':True,'input_tokens':len(ids),
                    'input_ids_sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest()}


class ReasoningGenerator(CausalGenerator):
    def __init__(self,config):
        self.reasoning_config=dict(config)
        super().__init__(config['model'],config['revision'],precision=config['precision'],max_new_tokens=config['max_new_tokens'])
        self.close_think_id=self.tokenizer.convert_tokens_to_ids('</think>')
        if type(self.close_think_id) is not int or self.close_think_id==self.tokenizer.unk_token_id:
            raise RuntimeError('Pinned tokenizer lacks the expected thinking boundary')
        self.request_seed=config['seed']

    def set_request_seed(self,seed):
        self.request_seed=seed

    def generate(self,system,user):
        self.last_generation={}
        self.torch.manual_seed(self.request_seed);self.torch.cuda.manual_seed_all(self.request_seed)
        inputs,audit=encode_reasoning_chat(self.tokenizer,system,user,return_tensors='pt')
        inputs=inputs.to('cuda');length=inputs['input_ids'].shape[-1]
        if length+self.max_new_tokens>self.model.config.max_position_embeddings:raise ValueError('Judge context limit exceeded')
        cfg=self.reasoning_config
        pad=self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id
        with self.torch.inference_mode():
            output=self.model.generate(**inputs,do_sample=True,temperature=cfg['temperature'],top_p=cfg['top_p'],
                top_k=cfg['top_k'],min_p=cfg['min_p'],max_new_tokens=self.max_new_tokens,pad_token_id=pad)
        ids=output[0,length:].tolist()
        final,split=extract_final_ids(ids,self.close_think_id)
        self.last_generation={**split,'chat_encoding':audit,'input_tokens':length,'output_tokens':len(ids),
                              'max_new_tokens':self.max_new_tokens,'reached_token_limit':len(ids)>=self.max_new_tokens,
                              'request_seed':self.request_seed,'thinking_text_retained':False}
        if final is None:return ''
        self.last_generation['final_tokens']=len(final)
        # Private reasoning is never decoded or stored; final JSON is preserved unedited.
        return self.tokenizer.decode(final,skip_special_tokens=True).strip()
