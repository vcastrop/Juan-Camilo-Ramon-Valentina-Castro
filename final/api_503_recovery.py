"""One explicit recovery after an archived HTTP 503 with zero model verdicts. No semantic resampling."""
from datetime import datetime,timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from final.gemini_judge_client import GeminiRESTGenerator,ApiFailure,validate_config
from final.prepare_eval_final import canonical_hash

ORIGINAL_SHA256='c59cf4064c5dab7888b480c4f4f012bdf7b52658292e87275d55fb4260bb20fe'
ORIGINAL_COMMIT='71912f1c5755790381a8e39c8a67801bcbf9243d'
VERSION='api-503-recovery-1'


def verify_previous(root):
    root=Path(root);path=root/'final/evidence/api_07/original_results.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ORIGINAL_SHA256:raise ValueError('Prior archive hash mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('Prior archive corrupted')
        meta=json.loads(z.read('metadata.json'));validate_config(meta['config'])
        rows=[json.loads(line) for line in z.read('raw_judgements.jsonl').decode().splitlines()]
        events=[json.loads(line) for line in z.read('api_requests.jsonl').decode().splitlines()]
        budget_bytes=z.read('budget_ledger_snapshot.json');budget=json.loads(budget_bytes)
    if meta['git_commit']!=ORIGINAL_COMMIT or meta['generation_http_calls']!=1 or meta['judgements_executed']!=1:
        raise ValueError('Recovery requires the fixed single-attempt run')
    if meta['status']!='stopped_api_or_format_failure' or meta['last_api_error']!={'code':'api_http_error','http_status':503}:
        raise ValueError('Recovery is authorized only for archived HTTP 503')
    if len(rows)!=1 or rows[0]['id']!='attribution_bad' or rows[0]['judgement']['score'] is not None:
        raise ValueError('Cannot recover by discarding valid model verdicts')
    if any(e['event']=='generation_response' for e in events) or meta.get('actual_model_version') is not None:
        raise ValueError('Prior run contains a model response; requires different audit')
    if hashlib.sha256(budget_bytes).hexdigest()!=meta['budget_ledger_snapshot_sha256']:raise ValueError('Prior budget snapshot mismatch')
    if budget.get('limit_usd')!='5.00' or len(budget.get('requests',{}))!=1:raise ValueError('Unexpected prior budget')
    entry=next(iter(budget['requests'].values()))
    if entry!={'status':'reserved_before_dispatch','charged_or_reserved_usd':'0.3072','worst_case_usd':'0.3072'}:
        raise ValueError('Original ambiguous-cost reservation must remain intact')
    if canonical_hash(json.loads((root/'final/gemini_calibration_config.json').read_text(encoding='utf-8')))!=meta['config_canonical_sha256']:
        raise ValueError('Candidate config changed')
    for name,expected in meta['source_hashes'].items():
        committed=subprocess.check_output(['git','show',ORIGINAL_COMMIT+':'+name],cwd=root)
        if hashlib.sha256(committed).hexdigest()!=expected:raise ValueError('Historical source hash mismatch')
        if (root/name).read_bytes().replace(b'\r\n',b'\n')!=committed.replace(b'\r\n',b'\n'):
            raise ValueError('Original model-facing implementation changed: '+name)
    return {'metadata':meta,'budget_snapshot':budget,'archive_sha256':ORIGINAL_SHA256,'version':VERSION}


def check_live_budget(folder,config,previous):
    folder=Path(folder);ledger=folder/'api_budget_ledger.json';marker=folder/'gemini_calibration_candidate_1.started.json'
    if not ledger.is_file() or not marker.is_file():raise ApiFailure('original_drive_ledger_and_marker_required_do_not_reset')
    if json.loads(ledger.read_text(encoding='utf-8'))!=previous['budget_snapshot']:
        raise ApiFailure('drive_budget_differs_from_archived_snapshot_requires_review')
    if json.loads(marker.read_text(encoding='utf-8')).get('config_sha256')!=canonical_hash(config):
        raise ApiFailure('original_experiment_marker_mismatch')


def register_recovery(folder,config,previous):
    check_live_budget(folder,config,previous)
    path=Path(folder)/'gemini_calibration_candidate_1_503_recovery.started.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'version':VERSION,
            'prior_archive_sha256':ORIGINAL_SHA256,'config_sha256':canonical_hash(config),
            'reason':'One explicit recovery of unavailable service with no prior model verdict',
            'original_reservation_retained':True,'automatic_transport_retries':0},stream,indent=2)
    return path


class RecoveryGeminiGenerator(GeminiRESTGenerator):
    def __init__(self,key,cfg,ledger_path,audit_path,*,previous,**kwargs):
        check_live_budget(Path(ledger_path).parent,cfg,previous)
        super().__init__(key,cfg,ledger_path,audit_path,**kwargs)
        self.previous=previous
        # The original reservation counts against the SAME USD 1 calibration sub-limit.
        # Do not reset stage_start to the prior reservation as if it were free new budget.
        self.stage_start=Decimal('0')

    def preflight(self):
        current=super().preflight()
        comparable=dict(current);prior=dict(self.previous['metadata']['model_preflight'])
        for item in [comparable,prior]:item['supportedGenerationMethods']=sorted(item['supportedGenerationMethods'])
        if comparable!=prior:raise ApiFailure('model_catalog_changed_requires_review')
        self.journal({'event':'explicit_503_recovery','prior_archive_sha256':ORIGINAL_SHA256,
            'original_reservation_retained':True,'no_prior_verdicts_discarded':True})
        return current
