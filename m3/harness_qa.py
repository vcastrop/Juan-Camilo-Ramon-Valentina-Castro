"""Versioned QA evaluation core; systems receive only questions, judges no gold.

Domain metric measures structural traceability, NOT semantic correctness.
No final evaluation is run by importing this module.
"""
import math
import re
import statistics
import time
import unicodedata
from collections import Counter
from judge import summarize_judgements

VERSION='m3-harness-qa-0.1-candidate'


def tokens(text):
    text=''.join(c for c in unicodedata.normalize('NFD',text.casefold()) if unicodedata.category(c)!='Mn')
    return re.findall(r'\w+',text,flags=re.UNICODE)


def token_f1(prediction,reference):
    """Multiset token F1, not embedding similarity or factual accuracy."""
    a,b=Counter(tokens(prediction)),Counter(tokens(reference))
    if not a or not b:
        return 0.0
    common=sum((a & b).values())
    return 2*common/(sum(a.values())+sum(b.values()))


def validate_cases(cases):
    if not isinstance(cases,list) or not cases:
        raise ValueError('Nonempty case list required')
    seen=set()
    for c in cases:
        for k in ['eval_id','input','expected','criterion','kind']:
            if not isinstance(c.get(k),str) or not c[k].strip():
                raise ValueError(f'Missing case field {k}')
        if c['eval_id'] in seen:
            raise ValueError('Duplicate eval_id')
        seen.add(c['eval_id'])
        if not isinstance(c.get('source_ids'),list) or any(not isinstance(x,str) or not x for x in c['source_ids']):
            raise ValueError('source_ids must be list of nonempty strings')
        if c['kind']!='unanswerable' and not c['source_ids']:
            raise ValueError('Answerable case must identify source documents')


def valid_output(output):
    return (isinstance(output,dict) and set(output)=={'respuesta','explicacion','citas','abstencion'}
            and all(isinstance(output[k],str) and output[k].strip() for k in ['respuesta','explicacion'])
            and type(output['abstencion']) is bool and isinstance(output['citas'],list)
            and all(isinstance(c,str) and c for c in output['citas']))


def domain_traceability(case,record):
    """Publicly named structural proxy; does NOT judge support or truth."""
    output=record.get('output')
    if not valid_output(output):
        return {'pass':False,'checks':{'valid_output':False},'semantic_review_required':True}
    contexts=record.get('contexts',[])
    by_id={c['chunk_id']:c for c in contexts if isinstance(c,dict) and isinstance(c.get('chunk_id'),str)}
    cited=output['citas']
    known=all(cid in by_id for cid in cited)
    traceable=known and all(isinstance(by_id[cid].get('text'),str) and by_id[cid]['text'].strip()
                          and isinstance(by_id[cid].get('source_url'),str) and by_id[cid]['source_url'].strip()
                          for cid in cited)
    cited_docs={by_id[cid].get('doc_id') for cid in cited if cid in by_id}
    expected_absence=case['kind']=='unanswerable'
    checks={'valid_output':True,'unique_context_ids':len(by_id)==len(contexts),
            'all_citations_traceable':bool(traceable),
            'abstention_mode_matches':output['abstencion']==expected_absence,
            'required_documents_cited':True if expected_absence else bool(cited) and set(case['source_ids']).issubset(cited_docs)}
    return {'pass':all(checks.values()),'checks':checks,'semantic_review_required':True}


def missing_judgement(error):
    return {'score':None,'reason':None,'score_adjusted':False,
            'attempts':[{'raw':None,'parse_error':None,'generation_error':error}]}


def harness(eval_set,system,judge):
    """Return per-case evidence + scorecard; system.predict gets question only.

    Judge must implement evaluate(record). None is allowed only for dry tests;
    result explicitly reports an incomplete scorecard when judgement is absent.
    """
    validate_cases(eval_set)
    rows=[]
    for case in eval_set:
        start=time.perf_counter(); error=None
        try:
            raw=system.predict(case['input'])
            if not isinstance(raw,dict):
                raise TypeError('predict must return a record dict')
            # Explicit whitelist excludes reference fields a system may attach.
            record={k:raw[k] for k in ['output','contexts','tool_trace','raw_response','parse_error','answer_attempts'] if k in raw}
            record['question']=case['input']
        except Exception as exc:
            error=f'{type(exc).__name__}: {exc}'
            record={'question':case['input'],'output':None,'contexts':[]}
        elapsed=time.perf_counter()-start
        output=record.get('output'); valid=valid_output(output)
        automatic=token_f1(output['respuesta'],case['expected']) if valid else 0.0
        domain=domain_traceability(case,record)
        try:
            judgement=judge.evaluate(record) if judge is not None else missing_judgement('Judge not configured')
            score=judgement.get('score')
            if score is not None and (type(score) is not int or not 1<=score<=5):
                raise ValueError('Invalid judge score')
        except Exception as exc:
            judgement=missing_judgement(f'{type(exc).__name__}: {exc}')
        rows.append({'eval_id':case['eval_id'],'kind':case['kind'],'record':record,
                     'system_error':error,'valid_output':bool(valid),'system_latency_seconds':elapsed,
                     'reference_token_f1':automatic,'domain_traceability':domain,'judgement':judgement})
    return {'harness_version':VERSION,'rows':rows,'scorecard':summarize(rows)}


def summarize(rows):
    if not rows:
        raise ValueError('Cannot summarize empty run')
    scores=summarize_judgements([r['judgement'] for r in rows])
    latencies=[r['system_latency_seconds'] for r in rows]
    if any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in latencies):
        raise ValueError('Invalid latency')
    n=len(rows)
    return {'total':n,'reference_token_f1_mean':statistics.mean(r['reference_token_f1'] for r in rows),
            'domain_traceability_rate':sum(r['domain_traceability']['pass'] for r in rows)/n,
            'valid_output_rate':sum(r['valid_output'] for r in rows)/n,
            'system_error_count':sum(r['system_error'] is not None for r in rows),
            'system_latency_median_seconds':statistics.median(latencies),'judge':scores,
            'all_judgements_available':scores['valid']==n,
            'quality_approved':False,'semantic_review_required':True}
