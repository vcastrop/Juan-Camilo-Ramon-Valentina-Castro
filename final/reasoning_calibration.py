"""Pilot first, same numeric regression thresholds; no cherry-picking of pilot scores."""
import hashlib
from final.calibration_final import cases,summarize
from final.judge_criteria import CHECKS,inconsistencies


def validate_config(config):
    fixed={'model':'Qwen/Qwen3-8B','revision':'b968826d9c46dd6066d109eabc6255188de91218',
           'precision':'nf4','compute_dtype':'float16','double_quantization':True,'enable_thinking':True,
           'do_sample':True,'temperature':0.6,'top_p':0.95,'top_k':20,'min_p':0.0,'max_new_tokens':4096,
           'seed':42,'pilot_fail_fast':True}
    if any(config.get(k)!=v for k,v in fixed.items()):raise ValueError('Reasoning trial differs from fixed candidate protocol')
    expected=['short_good','short_bad','number_bad','conflict_good','conflict_bad','empty_explanation_bad','citation_bad']
    if config.get('pilot_ids')!=expected:raise ValueError('Unexpected pilot schedule')


def judgement_issues(j,record):
    checks=j.get('checks')
    if not isinstance(checks,dict) or set(checks)!=set(CHECKS) or any(not isinstance(checks[k],str) or checks[k] not in values for k,values in CHECKS.items()):
        return ['invalid_or_missing_criteria']
    if type(j.get('score')) is not int or not 1<=j['score']<=5:return ['invalid_score']
    obj={'verificaciones':checks,'puntaje':j['score']}
    return sorted(set(j.get('internal_inconsistencies',[])+inconsistencies(obj,record)))


def request_seed(case_id,base=42):
    # Same per-anchor seed across lengths/mitigation conditions; no label enters the judge payload.
    return int.from_bytes(hashlib.sha256(f'{base}:{case_id}'.encode()).digest()[:4],'big')%(2**31)


def pilot_summary(rows,ids):
    anchors={c['id']:c for c in cases()}
    by_id={r['id']:r['judgement'] for r in rows}
    complete=len(rows)==len(ids) and len(by_id)==len(ids) and set(by_id)==set(ids)
    failures=[]
    for cid in ids:
        if cid not in by_id:continue
        j=by_id.get(cid,{})
        score=j.get('score');low,high=anchors[cid]['expected_score_range']
        if type(score) is not int or not low<=score<=high or judgement_issues(j,anchors[cid]['record']):
            failures.append(cid)
    return {'pilot_passed':complete and not failures,'expected_cases':len(ids),'cases':len(rows),'failed_ids':failures,
            'unexecuted_ids':[cid for cid in ids if cid not in by_id],
            'judge_validated_for_final':False,'pilot_scores_reused_for_main':True}


def full_summary(rows):
    base=summarize(rows)
    anchors={c['id']:c for c in cases()}
    missing=[{'id':r['id'],'condition':r['condition']} for r in rows if r['judgement'].get('checks') is None]
    inconsistent=[{'id':r['id'],'condition':r['condition'],'issues':judgement_issues(r['judgement'],anchors[r['id']]['record'])}
                  for r in rows if judgement_issues(r['judgement'],anchors[r['id']]['record'])]
    return {'calibration':base,'missing_checks':missing,'inconsistent_judgements':inconsistent,
            'gate_passed':base['gate_passed'] and not missing and not inconsistent,
            'confirmation_required':True,'human_semantic_audit_required':True,'judge_validated_for_final':False}
