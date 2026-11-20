"""Evaluate only eight changed saved packets. Existing USD7 ledger/notes stay intact."""
import argparse
from datetime import datetime,timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from final.evaluation21 import plan
from final.prepare_eval_final import canonical_hash
from final.product_judge14 import ProductGenerator,record_from_payload,POLICY as POLICY14
from final.hydrogen_judge_client import HydrogenRESTGenerator
from final.api_budget7 import BudgetLedger7
from final.judge_final import FinalJudge
from final.reasoning_calibration import request_seed
from final.gemini_judge_client import ApiFailure

MARKER='ocr_evaluation_21.started.json'


def financial_checkpoint():
    # Provenance of this archive is verified by evaluation21.plan -> product14 audit.
    with zipfile.ZipFile(ROOT/'final/evidence/product_14/original_results.zip') as z:
        return json.loads(z.read('budget_ledger_snapshot.json')),json.loads(z.read('metadata.json'))


def register(folder,p):
    folder=Path(folder)
    expected,meta=financial_checkpoint()
    current=json.loads((folder/'api_budget_ledger.json').read_text(encoding='utf-8'))
    if current!=expected:raise ValueError('Require exact post-product14 ledger; do not reset or hide other usage')
    if len(current['requests'])!=167 or current['limit_usd']!='7.00':raise ValueError('Wrong financial checkpoint')
    # Validate original backup/authorization and protected entries before any dispatch.
    BudgetLedger7(folder/'api_budget_ledger.json').used_or_reserved()
    (folder/'product_judge_14.started.json').read_bytes()
    marker={'version':'ocr-evaluation-21','plan_sha256':canonical_hash(p),
            'baseline_budget_sha256':canonical_hash(expected),'total_authorized_usd':'7.00',
            'new_cases':8,'outputs_regenerated':False,'automatic_transport_retries':0,
            'started_utc':datetime.now(timezone.utc).isoformat()}
    with (folder/MARKER).open('x',encoding='utf-8') as f:json.dump(marker,f,indent=2)
    return marker,meta


class EvaluationGenerator(ProductGenerator):
    def __init__(self,*args,plan_sha256,**kwargs):
        super().__init__(*args,**kwargs)
        marker=json.loads((self.ledger.path.parent/MARKER).read_text(encoding='utf-8'))
        if marker.get('plan_sha256')!=plan_sha256 or marker.get('total_authorized_usd')!='7.00':
            raise ValueError('Evaluation21 marker changed')
    def journal(self,entry):
        if entry.get('event')=='generation_response':self.observed_response_count+=1
        HydrogenRESTGenerator.journal(self,{**entry,'protocol':'ocr-evaluation-21',
            'billing_mode':POLICY14['billing_mode'],'free_project_attested':False,'authorized_total_usd':'7.00'})


def summary(jobs):
    valid=[j['judgement']['score'] for j in jobs if j.get('judgement') and j['judgement']['score'] is not None]
    return {'expected_cases':22,'valid_judgements':len(valid),'complete':len(jobs)==22 and len(valid)==22,
            'judge_mean_1_5':sum(valid)/22 if len(jobs)==22 and len(valid)==22 else None,
            'human_visual_review_pending':10,'domain_rate':None,'raw_scores_adjusted':False}


def run(output,budget,confirmed=False):
    output,budget=Path(output),Path(budget)
    if output.exists():raise ValueError('Do not repeat or overwrite this stage')
    output.mkdir(parents=True)
    jobs=[];generator=None
    meta={'status':'started','purpose':'eight_changed_saved_answers_only','generation_http_calls':0,
          'total_authorized_usd':'7.00','outputs_regenerated':False,'gold_in_judge_payload':False,
          'raw_scores_adjusted':False,'actual_invoice_verified':False,'automatic_transport_retries':0}
    try:
        if not confirmed:raise ApiFailure('same_paid_project_exclusive_use_total7_confirmation_required')
        if datetime.now(timezone.utc).date().isoformat()>POLICY14['price_recheck_after_utc']:raise ApiFailure('price_recheck_required')
        if not os.getenv('GEMINI_API_KEY'):raise ApiFailure('missing_api_key')
        p=plan()
        frozen=json.loads((ROOT/'final/evidence/evaluation21_plan.json').read_text(encoding='utf-8'))
        if p!=frozen:raise ValueError('Frozen plan differs')
        jobs=p['jobs']
        meta.update(plan_sha256=canonical_hash(p),source_archive_sha256=p['source_archive_sha256'],
                    reused_judge_cases=14,new_judge_cases=8,source_profile=p['profile'],
                    price_snapshot_utc=POLICY14['price_snapshot_utc'],price_recheck_after_utc=POLICY14['price_recheck_after_utc'])
        marker,old_meta=register(budget,p)
        cfg=json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'))
        generator=EvaluationGenerator(os.environ['GEMINI_API_KEY'],cfg,budget/'api_budget_ledger.json',
            output/'api_requests.jsonl',checkpoint={'metadata':old_meta},plan_sha256=canonical_hash(p),
            confirmed_paid_project=True,confirmed_total_usd7=True,exclusive_project_use=True)
        meta['model_preflight']=generator.preflight()
        with (output/'new_judgements.jsonl').open('x',encoding='utf-8') as f:
            for job in jobs:
                if job['judge_provenance']!='pending_new_evaluation':continue
                generator.set_request_seed(request_seed(job['id'],cfg['seed']))
                print('Judge changed saved case:',job['id'],flush=True)
                note=FinalJudge(generator).evaluate(record_from_payload(job['judge_payload']))
                job.update(judgement=note,judge_provenance='new_judgement_21')
                f.write(json.dumps({'id':job['id'],'payload_sha256':job['payload_sha256'],'judgement':note},ensure_ascii=False)+'\n');f.flush()
                if note['score'] is None:break
        meta['status']='completed_22_judgements_human_review_pending' if summary(jobs)['complete'] else 'stopped_partial_evidence_retained'
    except Exception as exc:
        meta.update(status='stopped_partial_evidence_retained',error_type=type(exc).__name__)
        if isinstance(exc,ApiFailure):meta.update(api_error_code=exc.code,http_status=exc.status)
    finally:
        if jobs:
            (output/'combined_judgements.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
            (output/'summary.json').write_text(json.dumps(summary(jobs),indent=2),encoding='utf-8')
        if generator:
            meta.update(generation_http_calls=generator.generation_calls,last_api_error=generator.last_error,
                        actual_model_version=generator.actual_version)
        try:
            if (budget/'api_budget_ledger.json').is_file():
                raw=(budget/'api_budget_ledger.json').read_bytes()
                (output/'budget_ledger_snapshot.json').write_bytes(raw)
                ledger=json.loads(raw)
                expected,_=financial_checkpoint()
                meta['prior_167_entries_unchanged']=all(ledger['requests'].get(k)==v for k,v in expected['requests'].items())
                meta['estimated_or_reserved_total_usd']=str(sum(Decimal(v['charged_or_reserved_usd']) for v in ledger['requests'].values()))
                meta['budget_ledger_snapshot_sha256']=hashlib.sha256(raw).hexdigest()
            for name in [MARKER,'api_budget_authorization_usd7.json','api_budget_ledger_before_usd7.json']:
                if (budget/name).is_file():(output/name).write_bytes((budget/name).read_bytes())
        except Exception as exc:
            meta.update(budget_snapshot_error_type=type(exc).__name__,status='stopped_budget_snapshot_error')
        meta['finished_utc']=datetime.now(timezone.utc).isoformat()
        (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--budget-dir',type=Path,required=True)
    p.add_argument('--confirm-same-paid-project-exclusive-total7',action='store_true');a=p.parse_args()
    result=run(a.output,a.budget_dir,a.confirm_same_paid_project_exclusive_total7)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['status']=='completed_22_judgements_human_review_pending' else 1)
