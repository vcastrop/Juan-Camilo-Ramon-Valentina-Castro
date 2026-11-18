"""Versioned literal-support judge; never replace or clamp a model score."""
import copy
import hashlib
import json
import time
from final.judge_criteria import SYSTEM,CHECKS,parse_final,inconsistencies,evidence_payload
from final.judge_final import RUBRIC,BIAS_CONTROL
from structured_output import parse_object

VERSION='literal-support-judge-1'
SUPPORT_INSTRUCTION='''
Verifica el campo solicitado, no solo que una palabra o cifra exista en algún lugar.
Una explicación que atribuye un dato al campo equivocado es falsa, no una omisión menor: merece 1 o 2 aunque la respuesta corta coincida. No confundas tipo con modalidad.
En abstencion usa no_aplica cuando output.abstencion es false; no penalices como abstención una conclusión prudente que no afirma fraude. En acusacion usa sin_respaldo solo si la salida realmente afirma una acusación no sustentada; no porque cualquier otra parte sea incorrecta.
Añade al JSON una clave soportes con exactamente dos objetos, uno por componente respuesta y explicacion. Cada objeto tiene solo componente, campo, chunk_id, cita_literal. Los tres últimos son cadenas o null. Cita texto CONTIGUO y EXACTO de un fragmento elegido por la salida; no reconstruyas cifras, no unas líneas separadas, no inventes palabras. La cita debe incluir el nombre del campo y el valor cuando ambos figuren juntos. El campo es el rótulo literal del fragmento, no el campo que desearías que figurara.
Si una afirmación es falsa, cita la evidencia que la contradice y márcala contradicha; no la declares sustentada porque su cifra aparezca en otro campo. Si no hay evidencia elegida por la salida, usa null. Una explicación vacía lleva sus tres campos null.
No escribas citas ni valores nuevos dentro de razon: explica brevemente la relación o el defecto; los textos comprobables van en soportes. La estructura final es verificaciones, soportes, puntaje, razon. Esta instrucción amplía la estructura anterior, no agrega otras claves.
'''


def collapse_exact_repetition(text):
    """Only collapse a full string made of >=2 byte-for-byte blocks separated by one space."""
    if not isinstance(text,str):return text
    for end,char in enumerate(text):
        if char!=' ':continue
        block=text[:end]
        if not block:continue
        unit=block+' '
        if (len(text)+1)%len(unit):continue
        repetitions=(len(text)+1)//len(unit)
        if repetitions>=2 and ' '.join([block]*repetitions)==text:return block
    return text


def normalized_record(record,enabled):
    result=copy.deepcopy(record);changes={}
    for key in ['respuesta','explicacion']:
        old=result.get('output',{}).get(key)
        new=collapse_exact_repetition(old) if enabled else old
        if old!=new:
            result['output'][key]=new
            changes[key]={'original_sha256':hashlib.sha256(old.encode()).hexdigest(),
                          'normalized_sha256':hashlib.sha256(new.encode()).hexdigest(),
                          'original_chars':len(old),'normalized_chars':len(new)}
    return result,changes


def parse_literal(raw):
    obj=parse_object(raw)
    if set(obj)!={'verificaciones','soportes','puntaje','razon'}:raise ValueError('Unexpected literal judgement fields')
    parse_final(json.dumps({k:v for k,v in obj.items() if k!='soportes'}))
    supports=obj['soportes']
    if not isinstance(supports,list) or len(supports)!=2:raise ValueError('Two support records required')
    if any(not isinstance(s,dict) or set(s)!={'componente','campo','chunk_id','cita_literal'} for s in supports):raise ValueError('Invalid support structure')
    if {s['componente'] for s in supports}!={'respuesta','explicacion'}:raise ValueError('Invalid support components')
    if any(s[k] is not None and not isinstance(s[k],str) for s in supports for k in ['campo','chunk_id','cita_literal']):raise ValueError('Support values must be string or null')
    return obj


def support_issues(obj,record):
    issues=[];contexts={c['chunk_id']:c['text'] for c in record.get('contexts',[])}
    cited=(record.get('output') or {}).get('citas',[])
    for s in obj['soportes']:
        component=s['componente'];cid=s['chunk_id'];quote=s['cita_literal'];field=s['campo']
        if cid is None and quote is None and field is None:
            if obj['verificaciones'][component]=='respaldada':issues.append(component+':supported_without_literal_evidence')
            continue
        if not cid or cid not in contexts or cid not in cited:issues.append(component+':unknown_or_uncited_chunk')
        elif not quote or quote not in contexts[cid]:issues.append(component+':nonliteral_quote')
        if field is not None and (not field or not quote or field not in quote):issues.append(component+':field_not_in_quote')
    return issues


class LiteralJudge:
    def __init__(self,generator,mitigate_verbosity=True):
        self.generator=generator;self.mitigate_verbosity=mitigate_verbosity
        schema={'verificaciones':{key:'|'.join(sorted(values)) for key,values in CHECKS.items()},
                'soportes':[{'componente':c,'campo':None,'chunk_id':None,'cita_literal':None} for c in ['respuesta','explicacion']],
                'puntaje':'ENTERO_ENTRE_1_Y_5','razon':'Justificación breve basada en evidencia'}
        self.system=SYSTEM.split('Devuelve un único JSON final')[0]+'\n'+SUPPORT_INSTRUCTION
        self.system+='\nDevuelve solo este esquema; elige un valor de cada enum (no barras), usa entero 1–5 y completa soportes con cadenas o null: '+json.dumps(schema,ensure_ascii=False)
        self.system+='\nRúbrica: '+json.dumps(RUBRIC,ensure_ascii=False)
        if mitigate_verbosity:self.system+='\n'+BIAS_CONTROL

    def evaluate(self,record):
        start=time.perf_counter();attempts=[];parsed=None
        normalized,changes=normalized_record(record,self.mitigate_verbosity)
        for index in range(2):
            packet=evidence_payload(normalized)
            if index:packet['correccion_de_formato']='Reemite un JSON con verificaciones, soportes, puntaje y razon; respeta las claves y tipos exigidos.'
            try:raw=self.generator.generate(self.system,json.dumps(packet,ensure_ascii=False))
            except Exception as exc:
                attempts.append({'raw_final':None,'generation_error':type(exc).__name__,'parse_error':None});break
            generation=dict(getattr(self.generator,'last_generation',{}))
            if generation.get('thinking_closed') is False or generation.get('reached_token_limit'):
                attempts.append({'raw_final':raw,'generation':generation,'generation_error':'incomplete_generation','parse_error':None});break
            try:parsed=parse_literal(raw);error=None
            except (ValueError,TypeError) as exc:error=str(exc)
            attempts.append({'raw_final':raw,'generation':generation,'parse_error':error,'generation_error':None})
            if parsed is not None:break
        issues=inconsistencies(parsed,normalized)+support_issues(parsed,normalized) if parsed else []
        return {'version':VERSION,'score':parsed['puntaje'] if parsed else None,'reason':parsed['razon'] if parsed else None,
                'checks':parsed['verificaciones'] if parsed else None,'supports':parsed['soportes'] if parsed else None,
                'internal_inconsistencies':issues,'attempts':attempts,'normalization':changes,
                'score_adjusted':False,'mitigate_verbosity':self.mitigate_verbosity,'latency_seconds':time.perf_counter()-start}
