"""Versioned transport diagnosis and accounting continuation; no semantic resampling."""
from datetime import datetime,timezone
from decimal import Decimal
import hashlib,json,socket,urllib.error,urllib.request,zipfile
from pathlib import Path
from final.hydrogen_resume import ResumableHydrogenGenerator,verify_checkpoint as verify09,safe_error_details
from final.hydrogen_judge_client import HydrogenRESTGenerator,MODEL
from final.hydrogen_history import check_drive
from final.gemini_judge_client import ApiFailure,NoRedirect
from final.prepare_eval_final import canonical_hash

SHA10='4e8d9f311ba4fdf83235cae8e69ba851b9161d5853e7613ddc657ce8039b9494'
POLICY={'version':'hydrogen-recovery-11','max_503_retries_total':1,'backoff_seconds':[60],
    'request_timeout_seconds':180,'calibration_estimate_limit_usd':'5.00','total_authorized_usd':'5.00',
    'generation_payload_changed':False,'billing_activated':False,'retry_transport_or_json':False}


def verify_checkpoint(root):
    root=Path(root);previous=verify09(root)
    path=root/'final/evidence/hydrogen_10/original_results.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA10:raise ValueError('Hydrogen10 archive changed')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('Hydrogen10 archive corrupted')
        meta=json.loads(z.read('metadata.json'));raw=z.read('budget_ledger_snapshot.json')
        rows=[json.loads(s) for s in z.read('raw_judgements.jsonl').decode().splitlines()]
    if meta['git_commit']!='4c404c9d2bcca3fae05225a2aa74a1d0462441c1' or meta['generation_http_calls']!=2:raise ValueError('Unexpected recovery provenance')
    if len(rows)!=2 or rows[0]['judgement']!=previous['saved_rows'][0]['judgement'] or rows[1]['judgement']['score'] is not None:raise ValueError('Do not discard valid notes')
    if hashlib.sha256(raw).hexdigest()!=meta['budget_ledger_snapshot_sha256']:raise ValueError('Budget snapshot mismatch')
    ledger=json.loads(raw)
    if len(ledger['requests'])!=6 or sum(Decimal(r['charged_or_reserved_usd']) for r in ledger['requests'].values())!=Decimal('2.4706725'):raise ValueError('Unexpected cumulative accounting')
    for key,value in previous['budget_snapshot']['requests'].items():
        if ledger['requests'].get(key)!=value:raise ValueError('Older reservation changed')
    previous['metadata']=meta
    previous['budget_snapshot']=ledger
    previous['base_drive']['budget_snapshot']=ledger
    previous['financial_checkpoint_archive_sha256']=SHA10
    return previous


def check_current_drive(folder,cfg,checkpoint):
    folder=Path(folder);check_drive(folder,checkpoint['base_drive'])
    for name in ['hydrogen_calibration_candidate_1.started.json','hydrogen_calibration_resume_1.started.json']:
        marker=folder/name
        if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('config_sha256')!=canonical_hash(cfg):
            raise ApiFailure('previous_hydrogen_marker_required')
    marker=json.loads((folder/'hydrogen_calibration_resume_1.started.json').read_text(encoding='utf-8'))
    if marker.get('checkpoint_sha256')!=checkpoint['archive_sha256']:raise ApiFailure('previous_resume_checkpoint_changed')


def register_resume(folder,cfg,checkpoint):
    check_current_drive(folder,cfg,checkpoint)
    path=Path(folder)/'hydrogen_calibration_resume_2.started.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'config_sha256':canonical_hash(cfg),
            'financial_checkpoint_archive_sha256':SHA10,'valid_notes_reused':1,'policy':POLICY},stream,indent=2)
    return path


class RecoveryGenerator(ResumableHydrogenGenerator):
    def __init__(self,key,cfg,ledger_path,audit_path,*,checkpoint,**kwargs):
        check_current_drive(Path(ledger_path).parent,cfg,checkpoint)
        super().__init__(key,cfg,ledger_path,audit_path,checkpoint=checkpoint,**kwargs)
        self.cfg['request_timeout_seconds']=POLICY['request_timeout_seconds']
        self.cfg['calibration_estimate_limit_usd']=POLICY['calibration_estimate_limit_usd']

    def failure(self,code,path,status=None,**details):
        self.provider_failure={'code':code,'http_status':status,'endpoint':path,**details}
        self.last_error=dict(self.provider_failure)
        self.journal({'event':'sanitized_transport_diagnostic',**self.provider_failure})
        raise ApiFailure(code,status) from None

    def _request(self,method,path,payload=None):
        if path not in {'models/'+MODEL,'models/'+MODEL+':countTokens','models/'+MODEL+':generateContent'}:raise ApiFailure('unexpected_endpoint')
        request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/'+path,
            data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None,
            headers={'x-goog-api-key':self._key,'Content-Type':'application/json'},method=method)
        try:
            with urllib.request.build_opener(NoRedirect()).open(request,timeout=self.cfg['request_timeout_seconds']) as response:
                status=getattr(response,'status',None)
                if type(status) is not int:status=None
                raw=response.read(2_000_001)
        except urllib.error.HTTPError as exc:
            try:info=safe_error_details(exc.read(8192),exc.headers)
            except Exception:info={'error_body_unavailable':True}
            finally:exc.close()
            self.failure('api_http_error',path,exc.code,**info)
        except (TimeoutError,socket.timeout):
            self.failure('api_timeout',path,timeout_seconds=self.cfg['request_timeout_seconds'])
        except urllib.error.URLError as exc:
            if isinstance(exc.reason,(TimeoutError,socket.timeout)):
                self.failure('api_timeout',path,timeout_seconds=self.cfg['request_timeout_seconds'])
            self.failure('api_network_error',path,network_reason_type=type(exc.reason).__name__)
        except OSError:
            self.failure('api_network_error',path)
        if len(raw)>2_000_000:self.failure('api_response_too_large',path,status)
        try:result=json.loads(raw.decode('utf-8'))
        except (UnicodeError,ValueError):self.failure('api_invalid_json_envelope',path,status)
        if not isinstance(result,dict):self.failure('api_envelope_not_object',path,status)
        return result

    def generate(self,system,user):
        local_retries=0
        while True:
            self.provider_failure=None;self.last_error=None
            try:
                # Invoke the original accounting/generation routine, not the old retry loop.
                result=HydrogenRESTGenerator.generate(self,system,user)
                self.last_generation['transient_503_retries_before_verdict']=local_retries
                self.last_error=None
                return result
            except ApiFailure as exc:
                self.last_error={'code':exc.code,'http_status':exc.status,**(self.provider_failure or {})}
                if exc.status!=503 or self.retry_count>=POLICY['max_503_retries_total']:raise
                if self.last_error.get('retry_after_seconds',0)>60:raise
                self.retry_count+=1;local_retries+=1
                self.journal({'event':'bounded_503_retry_scheduled','retry_number_global':self.retry_count,
                    'wait_seconds':60,'reservation_not_released':True,'valid_note_discarded':False})
                print('503 sin nota; espera 60 segundos. Unico reintento tecnico global.',flush=True)
                self.sleeper(60)
