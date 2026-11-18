"""Evaluator-only correction: uncited evidence may diagnose a bad citation, never support it."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from final.judge_literal import LiteralJudge,parse_literal
from final.judge_criteria import inconsistencies
from final.literal_calibration import PILOT_IDS,validate_config as validate_original
from final.reasoning_calibration import pilot_summary as base_pilot,full_summary as base_full
from final.calibration_final import cases,verbose
from final.prepare_eval_final import canonical_hash

VERSION='literal-support-evaluator-1.1'
ORIGINAL_SHA256='8bb33fbc240119aaabad4e250a2a394724efd528d1ad803d1bf58fdac0985f65'
ORIGINAL_COMMIT='6ec8dcdf22433c632b5eb0e5539401c33b9c923d'


def support_issues(obj,record):
    issues=[];contexts={c['chunk_id']:c['text'] for c in record.get('contexts',[])}
    cited=(record.get('output') or {}).get('citas',[])
    for s in obj['soportes']:
        component=s['componente'];cid=s['chunk_id'];quote=s['cita_literal'];field=s['campo']
        verdict=obj['verificaciones'][component]
        diagnostic=verdict in {'contradicha','incompleta','insuficiente'} and obj['verificaciones']['citas']=='no_respaldan'
        if cid is None and quote is None and field is None:
            if verdict=='respaldada':issues.append(component+':supported_without_literal_evidence')
            continue
        if not cid or cid not in contexts:issues.append(component+':unknown_chunk')
        else:
            if cid not in cited and not diagnostic:issues.append(component+':uncited_support_not_diagnostic')
            if not quote or quote not in contexts[cid]:issues.append(component+':nonliteral_quote')
        if field is not None and (not field or not quote or field not in quote):issues.append(component+':field_not_in_quote')
    return issues


def evaluate_saved(judgement,record):
    j=copy.deepcopy(judgement)
    obj={'verificaciones':j.get('checks'),'soportes':j.get('supports'),'puntaje':j.get('score'),'razon':j.get('reason')}
    j['historical_internal_inconsistencies']=list(j.get('historical_internal_inconsistencies',j.get('internal_inconsistencies',[])))
    try:
        parse_literal(json.dumps(obj))
        issues=inconsistencies(obj,record)+support_issues(obj,record)
    except (ValueError,TypeError):issues=['invalid_or_missing_literal_support']
    j['internal_inconsistencies']=sorted(set(issues))
    j['evaluation_version']=VERSION
    return j


def checked_rows(rows):
    anchors={c['id']:c['record'] for c in cases()};result=copy.deepcopy(rows)
    for row in result:
        record=anchors[row['id']]
        if row['condition'].endswith('verbose'):record=verbose(record)
        row['judgement']=evaluate_saved(row['judgement'],record)
    return result


def pilot_summary(rows,ids):return base_pilot(checked_rows(rows),ids)
def full_summary(rows):return base_full(checked_rows(rows))


def validate_config(config):
    if config.get('protocol')!='literal-support-continuation-1.1' or config.get('evaluation_version')!=VERSION:
        raise ValueError('Unexpected continuation protocol')
    if config.get('original_archive_sha256')!=ORIGINAL_SHA256:raise ValueError('Unexpected prior evidence')
    old=copy.deepcopy(config);old['protocol']='literal-support-reasoning-judge-1'
    validate_original(old)


class ContinuedLiteralJudge(LiteralJudge):
    """Original model/prompt/decoding unchanged; only evaluate its returned evidence differently."""
    def evaluate(self,record):return evaluate_saved(super().evaluate(record),record)


def load_previous(root):
    root=Path(root);path=root/'final/evidence/literal_05/original_results.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ORIGINAL_SHA256:raise ValueError('Prior archive hash mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('Corrupted prior archive')
        meta=json.loads(z.read('metadata.json'))
        if meta['git_commit']!=ORIGINAL_COMMIT:raise ValueError('Unexpected prior commit')
        validate_original(meta['config'])
        original_config=json.loads(subprocess.check_output(['git','show',ORIGINAL_COMMIT+':final/judge_literal_config.json'],cwd=root))
        if canonical_hash(original_config)!=meta['config_canonical_sha256'] or original_config!=meta['config']:
            raise ValueError('Prior config differs from committed config')
        for name,expected in meta['source_hashes'].items():
            data=subprocess.check_output(['git','show',ORIGINAL_COMMIT+':'+name],cwd=root)
            if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Prior source hash mismatch: '+name)
            # Guarantees same model-facing prompt/normalizer/generator code in continuation.
            if (root/name).read_bytes().replace(b'\r\n',b'\n')!=data.replace(b'\r\n',b'\n'):
                raise ValueError('Historical inference source changed: '+name)
        raw=[json.loads(line) for line in z.read('raw_judgements.jsonl').decode().splitlines()]
    if len(raw)!=7 or [r['id'] for r in raw]!=PILOT_IDS[:7] or any(r['condition']!='main_mitigated' or not r['pilot'] for r in raw):
        raise ValueError('Prior records are not the fixed seven-case prefix')
    rows=checked_rows(raw)
    if not pilot_summary(rows,PILOT_IDS[:7])['pilot_passed']:raise ValueError('Prior records fail corrected validation')
    for old,new in zip(raw,rows):
        if any(old['judgement'][k]!=new['judgement'][k] for k in ['score','reason','checks','supports','attempts']):
            raise ValueError('Original model judgement was altered')
        new['provenance']={'origin':'saved_literal_05','archive_sha256':ORIGINAL_SHA256,'commit':ORIGINAL_COMMIT,'regenerated':False}
    return rows,meta
