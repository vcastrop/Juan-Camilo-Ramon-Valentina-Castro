"""Candidate common harness: inference isolated from references; unknown judgement stays unknown."""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import time
import unicodedata
from final.prepare_eval_final import canonical_hash
from final.judge_criteria import evidence_payload
from final.score_visual_probe import percentile

VERSION='final-common-harness-candidate-1'
ROOT=Path(__file__).resolve().parents[1]


def normalize(text):
    text=unicodedata.normalize('NFKD',text.casefold())
    return ' '.join(''.join(c for c in text if not unicodedata.combining(c)).split())


def fact_present(fact,text):
    """Conservative literal diagnostic, not semantic correctness; no paraphrase fallback."""
    fact=normalize(str(fact));text=normalize(text)
    if not fact:return False
    if fact.isdigit():
        matches=[]
        for m in re.finditer(r'(?<![\w.,+\-])\d+(?:[.,]\d+)*(?!\w|[.,]\d)',text):
            token=m.group()
            integer=token if token.isdigit() else re.sub('[.,]','',token) if re.fullmatch(r'\d{1,3}(?:\.\d{3})+|\d{1,3}(?:,\d{3})+',token) else None
            if integer==fact:matches.append(m)
    else:
        matches=list(re.finditer(r'(?<!\w)'+re.escape(fact)+r'(?!\w)',text))
    for match in matches:
        clause=re.split(r'[;:\n!?]',text[:match.start()])[-1]
        prior=re.findall(r'\w+',clause)[-4:]
        if not {'no','ni','sin','tampoco','nunca'}.intersection(prior):return True
    return False


def valid_output(output):
    return (isinstance(output,dict) and set(output)=={'respuesta','explicacion','citas','abstencion'}
            and all(isinstance(output[k],str) for k in ['respuesta','explicacion'])
            and bool(output['respuesta'].strip()) and isinstance(output['citas'],list)
            and all(isinstance(c,str) and c for c in output['citas'])
            and len(output['citas'])==len(set(output['citas'])) and type(output['abstencion']) is bool)


def load_common(folder=None,root=ROOT):
    root=Path(root).resolve();folder=Path(folder or root/'final/eval/common_v1')
    inputs=json.loads((folder/'inputs.json').read_text(encoding='utf-8'))
    refs=json.loads((folder/'references.json').read_text(encoding='utf-8'))
    meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    for key,value in [('inputs',inputs),('references',refs)]:
        if canonical_hash(value)!=meta[key+'_canonical_sha256']:raise ValueError('Common package hash mismatch: '+key)
    if len(inputs)!=meta['cases'] or len(refs)!=len(inputs):raise ValueError('Incomplete common package')
    ids=[c['id'] for c in inputs];refids=[c['id'] for c in refs]
    if len(ids)!=len(set(ids)) or set(ids)!=set(refids):raise ValueError('Duplicate or mismatched IDs')
    for item in inputs:
        if not isinstance(item['question'],str) or not item['question'].strip():raise ValueError('Missing question')
        if item['image'] is not None:
            path=(root/item['image']).resolve()
            if not path.is_relative_to(root):raise ValueError('Image escapes repository')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=item['image_sha256']:raise ValueError('Image hash mismatch')
    return inputs,refs,meta


def infer(inputs,system,root=ROOT):
    """Only question/image cross the system boundary. No expected, criterion or judge result."""
    rows=[];seen=set();root=Path(root).resolve()
    for item in inputs:
        if item['id'] in seen:raise ValueError('Duplicate inference ID')
        seen.add(item['id']);start=time.perf_counter();error=None
        try:
            image=None
            if item.get('image') is not None:
                image=(root/item['image']).resolve()
                if not image.is_relative_to(root):raise ValueError('Image escapes repository')
                if hashlib.sha256(image.read_bytes()).hexdigest()!=item['image_sha256']:raise ValueError('Image hash mismatch')
            raw=system.predict(item['question'],image=image)
            if not isinstance(raw,dict):raise TypeError('System must return a record')
            record={k:copy.deepcopy(raw[k]) for k in ['output','contexts','tool_trace','visual','guard','components','source_consistency','answer_attempts','parse_error'] if k in raw}
            record['question']=item['question'];record.setdefault('contexts',[]);record.setdefault('tool_trace',[])
        except Exception as exc:
            error=type(exc).__name__ # Do not copy exception bodies that may contain credentials/input.
            record={'question':item['question'],'output':None,'contexts':[],'tool_trace':[]}
        rows.append({'id':item['id'],'record':record,'system_error_type':error,'wall_seconds':time.perf_counter()-start})
    return rows


def automatic(ref,record):
    output=record.get('output');valid=valid_output(output)
    result={'valid_output':valid,'literal_fact_coverage':0.0,'automatic_domain_checks_pass':False,
            'abstention_matches':False,'traceability_pass':False,'extraction_fields_exact':None}
    if not valid:return result
    abstained=output['abstencion'];expected=ref['expected_abstention']
    result['abstention_matches']=abstained==expected
    facts=ref['required_facts'];answer=output['respuesta']
    # Answer only: explanation mentioning a gold fact cannot rescue a wrong/abstaining answer.
    coverage=(1.0 if abstained else 0.0) if expected else (sum(fact_present(f,answer) for f in facts)/len(facts) if facts and not abstained else 0.0)
    raw_contexts=record.get('contexts',[])
    context_schema=isinstance(raw_contexts,list) and all(isinstance(c,dict) and all(isinstance(c.get(k),str) for k in ['chunk_id','doc_id','text']) for c in raw_contexts)
    contexts={c['chunk_id']:c for c in raw_contexts} if context_schema else {}
    context_schema=context_schema and len(contexts)==len(raw_contexts)
    citations=output['citas'];known=context_schema and all(c in contexts for c in citations)
    docs={contexts[c].get('doc_id') for c in citations if c in contexts}
    wanted=set(ref['source_ids'])
    if expected:trace=known
    elif ref['input_modality']=='image':trace=known and 'IMAGE::input' in citations
    else:trace=known and bool(citations) and wanted.issubset(docs) and not (docs-wanted)
    if ref['input_modality']=='image':
        visual=record.get('visual')
        extracted=visual.get('output') if isinstance(visual,dict) else None
        target=ref['expected_visual_fields']
        result['extraction_fields_exact']={k:isinstance(extracted,dict) and k in extracted and
            (normalize(extracted[k]) if isinstance(extracted[k],str) else extracted[k])==
            (normalize(v) if isinstance(v,str) else v) for k,v in target.items()}
    result.update(literal_fact_coverage=coverage,traceability_pass=bool(trace),
                  automatic_domain_checks_pass=bool(coverage==1 and result['abstention_matches'] and trace and output['explicacion'].strip()))
    return result


def judge_packet(record):
    # Rebuild a record from the whitelist, never hand reference-bearing dictionaries to a judge.
    packet=evidence_payload(record)
    return {'question':packet['pregunta'],'output':packet['respuesta_propuesta'],
            'contexts':packet['fragmentos'],'tool_trace':[{'tool_result':{'ok':True,**item}} for item in packet['calculos_verificables']]}


def evaluate(rows,references,judge=None):
    """Candidate protocol. All domain results remain unknown until validation integration is frozen."""
    refs={r['id']:r for r in references};seen=set();details=[]
    if len(refs)!=len(references):raise ValueError('Duplicate reference ID')
    for item in rows:
        cid=item['id']
        if cid in seen or cid not in refs:raise ValueError('Duplicate/unknown prediction ID')
        seen.add(cid);record=item['record'];ref=refs[cid];auto=automatic(ref,record)
        judgement=None;judge_error=None
        if judge is not None and auto['valid_output']:
            try:
                judgement=judge.evaluate(judge_packet(record))
                score=judgement.get('score')
                if score is not None and (type(score) is not int or not 1<=score<=5):raise ValueError('Invalid judge score')
            except Exception as exc:judgement=None;judge_error=type(exc).__name__
        details.append({'id':cid,'kind':ref['kind'],'input_modality':ref['input_modality'],**auto,
            'judge':judgement,'judge_error_type':judge_error,'domain_pass':None,
            'domain_status':'pending_validated_judge_and_frozen_domain_protocol',
            'system_error_type':item.get('system_error_type'),'wall_seconds':item.get('wall_seconds')})
    # Missing system rows remain failures in automatic denominator, not silently discarded.
    for cid in [r['id'] for r in references if r['id'] not in seen]:
        details.append({'id':cid,'kind':refs[cid]['kind'],'input_modality':refs[cid]['input_modality'],
            **automatic(refs[cid],{}),'judge':None,'judge_error_type':None,'domain_pass':None,
            'domain_status':'missing_prediction','system_error_type':'MissingPrediction','wall_seconds':None})
    by_id={d['id']:d for d in details};records={r['id']:r['record'] for r in rows}
    pairs=[]
    for ref in references:
        base=ref['pair_with']
        if base:
            left=records.get(ref['id'],{}).get('output');right=records.get(base,{}).get('output')
            equal=valid_output(left) and valid_output(right) and {k:normalize(left[k]) for k in ['respuesta','explicacion']}=={k:normalize(right[k]) for k in ['respuesta','explicacion']} and left['abstencion']==right['abstencion'] and set(left['citas'])==set(right['citas'])
            pairs.append({'id':ref['id'],'base':base,'output_invariant':bool(equal),
                          'both_automatic_checks_pass':by_id[ref['id']]['automatic_domain_checks_pass'] and by_id[base]['automatic_domain_checks_pass']})
    scores=[d['judge']['score'] for d in details if d['judge'] and d['judge'].get('score') is not None]
    times=[d['wall_seconds'] for d in details if type(d['wall_seconds']) in [int,float] and math.isfinite(d['wall_seconds']) and d['wall_seconds']>0]
    n=len(references)
    summary={'harness_version':VERSION,'case_count':n,'prediction_count':len(rows),
        'literal_fact_coverage_mean':sum(d['literal_fact_coverage'] for d in details)/n if n else None,
        'automatic_checks_rate':sum(d['automatic_domain_checks_pass'] for d in details)/n if n else None,
        'judge_mean_raw_experimental':sum(scores)/len(scores) if scores else None,'judge_valid_count':len(scores),
        'domain_compliance_rate':None,'judge_validated':False,'quality_accepted':False,
        'wall_p50_seconds':percentile(times,.5),'wall_p95_seconds':percentile(times,.95),'latency_count':len(times),
        'invariance_pairs':pairs,'warning':'Candidate: literal diagnostics are not semantic accuracy; domain protocol and judge validation pending. No efficiency acceptance.'}
    return details,summary


def harness(eval_set,system,judge=None,root=ROOT):
    inputs,refs,metadata=load_common(eval_set,root=root)
    predictions=infer(inputs,system,root=root)
    details,summary=evaluate(predictions,refs,judge)
    summary['eval_inputs_sha256']=metadata['inputs_canonical_sha256']
    summary['eval_references_sha256']=metadata['references_canonical_sha256']
    return {'predictions':predictions,'details':details,'scorecard':summary}
