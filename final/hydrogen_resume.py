"""Checkpointed continuation; at most two global technical 503 retries, never rescore a valid note."""
from datetime import datetime,timezone
from decimal import Decimal
import hashlib,json,re,secrets,subprocess,urllib.error,urllib.request,zipfile
from pathlib import Path
from final.hydrogen_judge_client import HydrogenRESTGenerator,MODEL
from final.gemini_judge_client import ApiFailure,NoRedirect
from final.hydrogen_history import verify_history
from final.prepare_eval_final import canonical_hash

SHA256='501f2ab9a2be78f599ff8b5468bc94597fb00de2d8b0621d89b7a16817a51c4f'
COMMIT='ece58275c2a19abfb6bbd2fe4b507731232e9083'
POLICY={'version':'hydrogen-resume-1','max_503_retries_total':2,'backoff_seconds':[30,60],
        'calibration_estimate_limit_usd':'3.50','total_authorized_usd':'5.00','generation_payload_changed':False}


def verify_checkpoint(root):
    root=Path(root);path=root/'final/evidence/hydrogen_09/original_results.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:raise ValueError('Checkpoint archive changed')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('Checkpoint archive corrupted')
        meta=json.loads(z.read('metadata.json'))
        rows=[json.loads(s) for s in z.read('raw_judgements.jsonl').decode().splitlines()]
        events=[json.loads(s) for s in z.read('api_requests.jsonl').decode().splitlines()]
        budget_bytes=z.read('budget_ledger_snapshot.json');snapshot=json.loads(budget_bytes)
    if meta['git_commit']!=COMMIT or meta['last_api_error'].get('http_status')!=503:raise ValueError('Unexpected checkpoint')
    if [r['id'] for r in rows]!=['attribution_bad','attribution_good'] or rows[0]['condition']!='main_mitigated':raise ValueError('Unexpected saved prefix')
    if type(rows[0]['judgement']['score']) is not int or rows[1]['judgement']['score'] is not None:raise ValueError('Do not discard valid verdicts')
    responses=[e for e in events if e['event']=='generation_response']
    if len(responses)!=1 or json.loads(responses[0]['raw_final'])['puntaje']!=rows[0]['judgement']['score']:
        raise ValueError('Saved score does not match public raw response')
    if hashlib.sha256(budget_bytes).hexdigest()!=meta['budget_ledger_snapshot_sha256']:raise ValueError('Checkpoint budget mismatch')
    if sum(Decimal(r['charged_or_reserved_usd']) for r in snapshot['requests'].values())!=Decimal('1.2418725'):
        raise ValueError('Unexpected accumulated reservation')
    if canonical_hash(json.loads((root/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8')))!=meta['config_canonical_sha256']:
        raise ValueError('Semantic/generation configuration changed')
    for name,expected in meta['source_hashes'].items():
        committed=subprocess.check_output(['git','show',COMMIT+':'+name],cwd=root)
        if hashlib.sha256(committed).hexdigest()!=expected or (root/name).read_bytes().replace(b'\r\n',b'\n')!=committed.replace(b'\r\n',b'\n'):
            raise ValueError('Frozen candidate implementation changed: '+name)
    previous=verify_history(root)
    for key,value in previous['budget_snapshot']['requests'].items():
        if snapshot['requests'].get(key)!=value:raise ValueError('Older reservation changed')
    result={'metadata':meta,'budget_snapshot':snapshot,'archive_sha256':SHA256,'saved_rows':rows[:1],
        'base_drive':{'metadata':previous['metadata'],'budget_snapshot':snapshot}}
    return result


def register_resume(folder,cfg,checkpoint):
    folder=Path(folder)
    from final.hydrogen_history import check_drive
    check_drive(folder,checkpoint['base_drive'])
    marker=folder/'hydrogen_calibration_candidate_1.started.json'
    if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('config_sha256')!=canonical_hash(cfg):
        raise ApiFailure('original_hydrogen_marker_required')
    path=folder/'hydrogen_calibration_resume_1.started.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'checkpoint_sha256':SHA256,
                   'config_sha256':canonical_hash(cfg),'policy':POLICY,'valid_notes_reused':1},stream,indent=2)
    return path


def safe_error_details(payload,headers):
    """Retain codes/categories, never provider message bodies or echoed credentials/input."""
    details={}
    try:
        error=json.loads(payload).get('error',{})
        status=error.get('status')
        if isinstance(status,str) and re.fullmatch('[A-Z_]{1,80}',status):details['provider_status']=status
        message=str(error.get('message','')).casefold()
        for keyword,category in [('overload','overload'),('capacity','capacity'),('quota','quota'),('api key','api_key'),('billing','billing'),('region','region')]:
            if keyword in message:details['provider_message_category']=category;break
    except (ValueError,TypeError,AttributeError):pass
    raw=headers.get('Retry-After','') if headers else ''
    if isinstance(raw,str) and raw.isdigit() and int(raw)<=3600:details['retry_after_seconds']=int(raw)
    return details


class ResumableHydrogenGenerator(HydrogenRESTGenerator):
    def __init__(self,key,cfg,ledger_path,audit_path,*,checkpoint,jitter=None,**kwargs):
        super().__init__(key,cfg,ledger_path,audit_path,previous=checkpoint['base_drive'],**kwargs)
        self.checkpoint=checkpoint
        self.cfg['calibration_estimate_limit_usd']=POLICY['calibration_estimate_limit_usd']
        self.actual_version=checkpoint['metadata']['actual_model_version']
        self.retry_count=0;self.provider_failure=None;self.jitter=jitter or (lambda:secrets.randbelow(1000)/1000)

    def preflight(self):
        current=super().preflight();before=dict(self.checkpoint['metadata']['model_preflight']);after=dict(current)
        for info in [before,after]:info['supportedGenerationMethods']=sorted(info['supportedGenerationMethods'])
        if before!=after:raise ApiFailure('catalog_changed_since_checkpoint')
        return current

    def _request(self,method,path,payload=None):
        allowed={'models/'+MODEL,'models/'+MODEL+':countTokens','models/'+MODEL+':generateContent'}
        if path not in allowed:raise ApiFailure('unexpected_endpoint')
        request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/'+path,
            data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None,
            headers={'x-goog-api-key':self._key,'Content-Type':'application/json'},method=method)
        try:
            with urllib.request.build_opener(NoRedirect()).open(request,timeout=self.cfg['request_timeout_seconds']) as response:
                return json.loads(response.read(2_000_001).decode('utf-8'))
        except urllib.error.HTTPError as exc:
            info=safe_error_details(exc.read(8192),exc.headers)
            self.provider_failure={'code':'api_http_error','http_status':exc.code,'endpoint':path,**info}
            self.last_error=dict(self.provider_failure)
            self.journal({'event':'provider_http_failure',**self.provider_failure})
            raise ApiFailure('api_http_error',exc.code) from None
        except Exception:raise ApiFailure('api_transport_or_json_error') from None

    def generate(self,system,user):
        local_retries=0
        while True:
            self.provider_failure=None;self.last_error=None
            try:
                result=super().generate(system,user)
                self.last_generation['transient_503_retries_before_verdict']=local_retries
                self.last_error=None
                return result
            except ApiFailure as exc:
                info={'code':exc.code,'http_status':exc.status}
                if self.provider_failure:info.update(self.provider_failure)
                self.last_error=info
                if exc.status!=503 or self.retry_count>=POLICY['max_503_retries_total']:raise
                server_delay=info.get('retry_after_seconds',0)
                if server_delay>60:raise
                delay=min(60,max(POLICY['backoff_seconds'][self.retry_count]+self.jitter(),server_delay))
                self.retry_count+=1;local_retries+=1
                self.journal({'event':'bounded_503_retry_scheduled','retry_number_global':self.retry_count,
                    'wait_seconds':delay,'no_valid_verdict_discarded':True,'reservation_not_released':True})
                print('503 sin respuesta; espera controlada:',round(delay,1),'s; reintento técnico',self.retry_count,'de 2.',flush=True)
                self.sleeper(delay)
