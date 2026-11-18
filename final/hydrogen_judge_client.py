"""Bounded REST client for synthetic calibration. No SDK retries or credential-bearing URLs."""
from datetime import datetime,timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from final.api_budget import BudgetLedger,money
from final.hydrogen_history import check_drive

MODEL='gemini-4-hydrogen'
SCHEMA={'type':'object','properties':{'puntaje':{'type':'integer','minimum':1,'maximum':5},
    'razon':{'type':'string'}},'required':['puntaje','razon'],'additionalProperties':False}


from final.gemini_judge_client import ApiFailure,NoRedirect


def validate_config(cfg):
    fixed={'protocol':'hydrogen-calibration-candidate-1','model':MODEL,'api_version':'v1beta',
        'billing_mode':'free_project_attested_only','seed':42,'thinking_level':'HIGH','include_thoughts':False,
        'max_output_tokens':65536,'input_count_limit':16384,'automatic_transport_retries':0,
        'max_generation_attempts_per_judgement':2,'pilot_fail_fast':True,'total_authorized_usd':'5.00',
        'calibration_estimate_limit_usd':'2.00','input_price_per_million_usd':'1.50','output_price_per_million_usd':'7.50',
        'minimum_generation_interval_seconds':20,'request_timeout_seconds':90,
        'price_snapshot_utc':'2026-11-18','price_recheck_after_utc':'2026-11-20'}
    if any(cfg.get(k)!=v for k,v in fixed.items()):raise ValueError('API candidate differs from fixed protocol')
    pilot=['attribution_bad','attribution_good','short_good','short_bad','number_bad','conflict_good','conflict_bad','empty_explanation_bad','citation_bad']
    if cfg.get('pilot_ids')!=pilot:raise ValueError('Unexpected pilot schedule')


def public_response(response):
    candidates=response.get('candidates',[])
    if len(candidates)!=1:raise ApiFailure('missing_or_multiple_candidates')
    candidate=candidates[0]
    text=''.join(p['text'] for p in candidate.get('content',{}).get('parts',[]) if not p.get('thought') and isinstance(p.get('text'),str))
    return text,candidate.get('finishReason')


class HydrogenRESTGenerator:
    def __init__(self,key,cfg,ledger_path,audit_path,confirmed_free_project=False,transport=None,clock=time.monotonic,sleeper=time.sleep,now_utc=None,previous=None):
        validate_config(cfg)
        if not confirmed_free_project:raise ApiFailure('free_project_confirmation_required')
        if not isinstance(key,str) or not key.strip():raise ApiFailure('missing_api_key')
        if (now_utc or datetime.now(timezone.utc)).date().isoformat()>cfg['price_recheck_after_utc']:raise ApiFailure('price_recheck_required')
        if previous is None:raise ApiFailure('prior_accounting_required')
        check_drive(Path(ledger_path).parent,previous)
        self._key=key;self.cfg=dict(cfg);self.ledger=BudgetLedger(ledger_path);self.audit_path=Path(audit_path)
        self.audit_path.parent.mkdir(parents=True,exist_ok=True)
        self.stage_start=Decimal(0);self.clock=clock;self.sleeper=sleeper
        self.transport=transport or self._request;self.last_dispatch=None;self.model_info=None;self.actual_version=None
        self.request_seed=cfg['seed'];self.last_generation={};self.generation_calls=0;self.last_error=None

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
            self.last_error={'code':'api_http_error','http_status':exc.code,'endpoint':path}
            self.journal({'event':'http_failure','endpoint':path,'status':exc.code,'automatic_retry':False})
            raise ApiFailure('api_http_error',exc.code) from None
        except Exception:
            self.last_error={'code':'api_transport_or_json_error','endpoint':path}
            self.journal({'event':'transport_or_json_failure','endpoint':path,'automatic_retry':False})
            raise ApiFailure('api_transport_or_json_error') from None

    def journal(self,entry):
        with self.audit_path.open('a',encoding='utf-8') as stream:stream.write(json.dumps(entry,ensure_ascii=False)+'\n')

    def preflight(self):
        info=self.transport('GET','models/'+MODEL,None)
        if info.get('name')!='models/'+MODEL:raise ApiFailure('unexpected_model_name')
        if not {'generateContent','countTokens'}.issubset(info.get('supportedGenerationMethods',[])):raise ApiFailure('model_methods_unavailable')
        limit=info.get('outputTokenLimit')
        if type(limit) is not int or not self.cfg['max_output_tokens']<=limit<=1048576:raise ApiFailure('unexpected_model_output_limit')
        self.model_info={k:info[k] for k in ['name','version','inputTokenLimit','outputTokenLimit','supportedGenerationMethods'] if k in info}
        self.journal({'event':'model_preflight','model':self.model_info})
        return self.model_info

    def set_request_seed(self,seed):self.request_seed=seed

    def request_body(self,system,user):
        return {'systemInstruction':{'parts':[{'text':system}]},
            'contents':[{'role':'user','parts':[{'text':user}]}],
            'generationConfig':{'maxOutputTokens':self.cfg['max_output_tokens'],
                'seed':self.request_seed,'responseMimeType':'application/json','responseJsonSchema':SCHEMA,
                'thinkingConfig':{'thinkingLevel':self.cfg['thinking_level'],'includeThoughts':False}}}

    def generate(self,system,user):
        self.last_generation={}
        if self.model_info is None:raise ApiFailure('preflight_required')
        if len(system.encode())+len(user.encode())>64000:raise ApiFailure('input_byte_limit')
        body=self.request_body(system,user)
        counted=self.transport('POST','models/'+MODEL+':countTokens',{'generateContentRequest':{'model':'models/'+MODEL,**body}})
        count=counted.get('totalTokens')
        if type(count) is not int or not 0<count<=self.cfg['input_count_limit']:raise ApiFailure('invalid_or_excessive_input_count')
        # Reserve the FULL advertised model output limit, including potential thought tokens.
        # countTokens is an estimate (schema/overhead may differ), so reserve the whole small-input cap too.
        reservation=Decimal(self.cfg['input_count_limit']+self.cfg['max_output_tokens'])*max(
            money(self.cfg['input_price_per_million_usd']),money(self.cfg['output_price_per_million_usd']))/Decimal(1_000_000)
        if self.ledger.used_or_reserved()-self.stage_start+reservation>money(self.cfg['calibration_estimate_limit_usd']):
            raise ApiFailure('calibration_estimate_budget_exhausted')
        if self.last_dispatch is not None:
            self.sleeper(max(0,self.cfg['minimum_generation_interval_seconds']-(self.clock()-self.last_dispatch)))
        request_id=self.ledger.reserve(reservation);self.last_dispatch=self.clock();self.generation_calls+=1
        base={'request_id':request_id,'model_requested':MODEL,'input_tokens_counted':count,'seed_requested':self.request_seed,
              'reserved_estimate_usd':str(reservation),'request_sha256':hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
        try:
            response=self.transport('POST','models/'+MODEL+':generateContent',body)
            text,finish=public_response(response)
            usage=response.get('usageMetadata',{});total=usage.get('totalTokenCount');prompt=usage.get('promptTokenCount')
            if type(total) is not int or type(prompt) is not int or not 0<=prompt<=total:raise ApiFailure('missing_or_invalid_usage')
            if prompt>self.cfg['input_count_limit']:raise ApiFailure('actual_input_exceeded_count_cap')
            # Count all tokens at output tariff: conservative estimate, not an invoice/payment.
            estimated_upper=Decimal(total)*money(self.cfg['output_price_per_million_usd'])/Decimal(1_000_000)
            self.ledger.settle(request_id,estimated_upper)
            version=response.get('modelVersion')
            if not isinstance(version,str) or not (version==MODEL or version.startswith(MODEL+'-')):raise ApiFailure('unexpected_response_model_version')
            if self.actual_version is not None and version!=self.actual_version:raise ApiFailure('model_version_changed_during_run')
            self.actual_version=version
            self.last_generation={**base,'model_version':version,'finish_reason':finish,'usage_metadata':usage,
                'estimated_upper_cost_usd':str(estimated_upper),'free_project_attested':True,
                'actual_invoice_verified':False,'thinking_text_retained':False}
            self.journal({'event':'generation_response',**self.last_generation,'raw_final':text})
            if finish!='STOP':raise ApiFailure('generation_not_complete')
            return text
        except Exception as exc:
            self.last_error={'code':exc.code if isinstance(exc,ApiFailure) else type(exc).__name__,
                             'http_status':getattr(exc,'status',None)}
            self.journal({'event':'generation_failed',**base,
                'code':exc.code if isinstance(exc,ApiFailure) else type(exc).__name__,
                'http_status':getattr(exc,'status',None),'cost_unknown_or_reserved':True})
            if isinstance(exc,ApiFailure):raise
            raise ApiFailure('generation_or_budget_validation_error') from None
