"""Fail-closed acceptance of paired measured evidence. No measurements/model scores fabricated."""
import hashlib
import json
import math
from pathlib import Path
import re
from fractions import Fraction

POLICY_PATH=Path(__file__).with_name('efficiency_policy.json')
SHARED_HASHES=['eval_set_sha256','harness_sha256','judge_config_sha256','judge_calibration_sha256','shared_inference_config_sha256','policy_sha256']


def policy_fingerprint(policy):
    return hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def validate(profile):
    issues=[]
    for key in SHARED_HASHES:
        if not isinstance(profile.get(key),str) or not re.fullmatch('[a-f0-9]{64}',profile[key]):
            issues.append('missing_or_invalid_'+key)
    if profile.get('judge_calibration_passed') is not True:
        issues.append('judge_not_calibrated')
    if not isinstance(profile.get('hardware_fingerprint'),dict) or not profile['hardware_fingerprint']:
        issues.append('hardware_not_identified')
    rows=profile.get('rows')
    if not isinstance(rows,list) or not rows:
        return issues+['no_case_rows']
    seen=set()
    for row in rows:
        if not isinstance(row,dict):
            issues.append('invalid_row'); continue
        case_id=row.get('id')
        if not isinstance(case_id,str) or not case_id or case_id in seen:
            issues.append('missing_or_duplicate_id')
        if isinstance(case_id,str): seen.add(case_id)
        if type(row.get('domain_pass')) is not bool:
            issues.append('unknown_domain_result')
        critical=row.get('critical_failures')
        if not isinstance(critical,list) or any(not isinstance(x,str) or not x for x in critical):
            issues.append('unknown_critical_failures')
        controls=row.get('controls')
        if not isinstance(controls,dict) or any(not isinstance(k,str) or type(v) is not bool for k,v in controls.items()):
            issues.append('unknown_controls')
        memory=row.get('peak_cuda_allocated_bytes')
        if type(memory) is not int or memory<=0:
            issues.append('invalid_memory')
        latency=row.get('wall_seconds')
        if type(latency) not in [int,float] or not math.isfinite(latency) or latency<=0:
            issues.append('invalid_latency')
    return sorted(set(issues))


def assess(before,after,policy=None):
    policy=policy or json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    result={'policy_version':policy['version'],'policy_sha256':policy_fingerprint(policy),
            'status':'not_evaluable','accepted':False,'reasons':[],
            'warning':policy['readiness_warning']}
    for name,profile in [('before',before),('after',after)]:
        result['reasons'].extend(name+':'+x for x in validate(profile))
    if result['reasons']: return result
    for key in SHARED_HASHES+['hardware_fingerprint']:
        if before[key]!=after[key]: result['reasons'].append('unmatched_'+key)
    if before['policy_sha256']!=result['policy_sha256'] or after['policy_sha256']!=result['policy_sha256']:
        result['reasons'].append('policy_differs_from_predeclared_rules')
    if before.get('profile')!='fp16' or after.get('profile')!='nf4_generator' or after.get('quantization_verified') is not True:
        result['reasons'].append('quantization_not_verified')
    left={r['id']:r for r in before['rows']};right={r['id']:r for r in after['rows']}
    if set(left)!=set(right): result['reasons'].append('unmatched_case_ids')
    if result['reasons']: return result
    measured_controls={key for row in left.values() for key in row['controls']}
    if not {'abstention','adversarial','invariance'}.issubset(measured_controls):
        result['reasons'].append('required_controls_not_measured')
        return result
    for case_id in left:
        if set(left[case_id]['controls'])!=set(right[case_id]['controls']):
            result['reasons'].append('unmatched_control_definitions:'+case_id)
    if result['reasons']: return result
    count=len(left)
    before_rate=Fraction(sum(r['domain_pass'] for r in left.values()),count)
    after_rate=Fraction(sum(r['domain_pass'] for r in right.values()),count)
    base_peak=max(r['peak_cuda_allocated_bytes'] for r in left.values())
    efficient_peak=max(r['peak_cuda_allocated_bytes'] for r in right.values())
    saving=Fraction(base_peak-efficient_peak,base_peak)
    new_critical=[{'id':cid,'type':kind} for cid in left
                  for kind in sorted(set(right[cid]['critical_failures'])-set(left[cid]['critical_failures']))]
    regressions=[{'id':cid,'control':key} for cid in left for key,value in left[cid]['controls'].items()
                 if value and not right[cid]['controls'][key]]
    result.update(case_count=count,domain_before=float(before_rate),domain_after=float(after_rate),
                  domain_drop_percentage_points=float(100*(before_rate-after_rate)),
                  peak_before_bytes=base_peak,peak_after_bytes=efficient_peak,
                  peak_memory_reduction_fraction=float(saving),new_critical_failures=new_critical,
                  control_regressions=regressions)
    if before_rate-after_rate>Fraction(policy['max_domain_drop_absolute']):
        result['reasons'].append('domain_drop_exceeds_limit')
    if len(new_critical)>policy['max_new_critical_failures']:
        result['reasons'].append('new_critical_failures')
    if len(regressions)>policy['max_control_regressions']:
        result['reasons'].append('control_regressions')
    if saving<Fraction(policy['min_peak_cuda_memory_reduction']):
        result['reasons'].append('insufficient_memory_reduction')
    result['accepted']=not result['reasons']
    result['status']='accepted_relative_efficiency' if result['accepted'] else 'rejected'
    return result
