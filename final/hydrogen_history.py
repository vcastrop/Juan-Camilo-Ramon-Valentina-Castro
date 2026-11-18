"""Preserve both unavailable-service attempts and their reservations before changing model."""
from datetime import datetime,timezone
import hashlib,json,subprocess,zipfile
from pathlib import Path
from final.gemini_judge_client import ApiFailure
from final.prepare_eval_final import canonical_hash

SHA256='2ad8056f6b266783233dd5d1f144544a454e3571a304404ddb4a8e6afaf69e0e'
COMMIT='7afdda0212bf38ad1accd043a968db722569c618'


def verify_history(root):
    root=Path(root);path=root/'final/evidence/api_08/original_results.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:raise ValueError('API 08 evidence changed')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('API 08 evidence corrupted')
        meta=json.loads(z.read('metadata.json'))
        rows=[json.loads(s) for s in z.read('raw_judgements.jsonl').decode().splitlines()]
        journal=[json.loads(s) for s in z.read('api_requests.jsonl').decode().splitlines()]
        snapshot=z.read('budget_ledger_snapshot.json');ledger=json.loads(snapshot)
    if meta['git_commit']!=COMMIT or meta['last_api_error'].get('http_status')!=503:
        raise ValueError('Unexpected model-change provenance')
    if len(rows)!=1 or rows[0]['judgement']['score'] is not None or any(e['event']=='generation_response' for e in journal):
        raise ValueError('Prior model returned a verdict; do not select between verdicts')
    if meta['generation_http_calls']!=1 or meta['historical_generation_http_calls']!=1:
        raise ValueError('Expected exactly two prior generation attempts')
    if hashlib.sha256(snapshot).hexdigest()!=meta['budget_ledger_snapshot_sha256']:raise ValueError('Budget snapshot hash mismatch')
    if len(ledger.get('requests',{}))!=2 or ledger.get('limit_usd')!='5.00':raise ValueError('Unexpected prior accounting')
    for r in ledger['requests'].values():
        if r!={'status':'reserved_before_dispatch','charged_or_reserved_usd':'0.3072','worst_case_usd':'0.3072'}:
            raise ValueError('Prior reservations cannot be released silently')
    for name,expected in meta['source_hashes'].items():
        committed=subprocess.check_output(['git','show',COMMIT+':'+name],cwd=root)
        if hashlib.sha256(committed).hexdigest()!=expected:raise ValueError('Prior source provenance mismatch')
    return {'archive_sha256':SHA256,'metadata':meta,'budget_snapshot':ledger}


def check_drive(folder,previous):
    folder=Path(folder);path=folder/'api_budget_ledger.json'
    if not path.is_file() or json.loads(path.read_text(encoding='utf-8'))!=previous['budget_snapshot']:
        raise ApiFailure('same_drive_accounting_required_do_not_reset')
    for name in ['gemini_calibration_candidate_1.started.json','gemini_calibration_candidate_1_503_recovery.started.json']:
        marker=folder/name
        if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('config_sha256')!=previous['metadata']['config_canonical_sha256']:
            raise ApiFailure('prior_drive_marker_missing_or_changed')


def register_hydrogen(folder,config,previous):
    check_drive(folder,previous)
    path=Path(folder)/'hydrogen_calibration_candidate_1.started.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'config_sha256':canonical_hash(config),
            'prior_archive_sha256':SHA256,'previous_reservations_retained':True,
            'note':'New model after two HTTP 503 and zero verdicts, not selection of favourable notes'},stream,indent=2)
    return path
