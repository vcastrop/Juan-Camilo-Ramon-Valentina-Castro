"""Native chat encoding with no duplicated special tokens; validates exact token equivalence."""
import hashlib
import json

PROTOCOL='native-chat-1'


def encode_chat(tokenizer,system,user,return_tensors=None):
    messages=[{'role':'system','content':system},{'role':'user','content':user}]
    text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    kwargs={'add_special_tokens':False}
    if return_tensors is not None:kwargs['return_tensors']=return_tensors
    encoded=tokenizer(text,**kwargs)
    ids=encoded['input_ids']
    if hasattr(ids,'tolist'):ids=ids.tolist()
    if len(ids)==1 and isinstance(ids[0],list):ids=ids[0]
    native=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True)
    if not isinstance(ids,list) or any(type(i) is not int for i in ids) or ids!=native:
        raise ValueError('Encoded tokens differ from the native chat template')
    bos=getattr(tokenizer,'bos_token_id',None)
    prefix=0
    if bos is not None:
        for token in ids:
            if token!=bos:break
            prefix+=1
    audit={'protocol':PROTOCOL,'add_special_tokens':False,'native_equivalent':True,
           'input_token_count':len(ids),'leading_bos_count':prefix,
           'input_ids_sha256':hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()}
    return encoded,audit
