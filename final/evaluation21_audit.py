"""Offline receipt and unchanged-rule semantic join for the completed OCR profile."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from final.evaluation21 import ROOT, plan, PROFILE
from final.prepare_eval_final import canonical_hash
from final.run_evaluation21 import financial_checkpoint, summary
from final.visual21_receipt import receipt
from final.domain_scorecard14 import join_row
from final.common_harness import load_common

ZIP_SHA='f47d0584e6048c6117cc2b60b0c39b093edbfa9ec0aac1a0ff4d53e9fbb94fbd'
NB_SHA='3856f0572831700672c121ff388e691d7eab519295220fe7b07efbbc189ac2eb'


def audit(root=ROOT):
    root=Path(root);folder=root/'final/evidence/evaluation21_completed'
    archive=folder/'original_results.zip';nb_raw=(folder/'executed.ipynb').read_bytes()
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=ZIP_SHA or hashlib.sha256(nb_raw).hexdigest()!=NB_SHA:
        raise ValueError('Original receipt changed')
    with zipfile.ZipFile(archive) as z:
        if len(set(z.namelist()))!=len(z.namelist()):raise ValueError('Duplicate archive members')
        files={n:z.read(n) for n in z.namelist()}
    def read(name):return json.loads(files['evaluation21_results/'+name])
    meta=read('metadata.json');jobs=read('combined_judgements.json');p=plan(root)
    commit=files['checkout_commit.txt'].decode().strip()
    if commit!='576a51112cd1f774785a68821cae98285bdfbe86':raise ValueError('Unexpected execution checkout')
    original=json.loads(subprocess.check_output(['git','show',commit+':final/ContractRisk_Final_Evaluacion_21_Colab.ipynb'],cwd=root))
    nb=json.loads(nb_raw)
    source=lambda n:[''.join(c['source']).strip() for c in n['cells'] if c['cell_type']=='code']
    if source(nb)!=source(original) or any(c.get('execution_count') is None for c in nb['cells'] if c['cell_type']=='code'):
        raise ValueError('Executed code differs or is incomplete')
    if any(o.get('output_type')=='error' for c in nb['cells'] for o in c.get('outputs',[])):
        raise ValueError('Notebook contains errors')
    if meta['status']!='completed_22_judgements_human_review_pending' or meta['generation_http_calls']!=8:
        raise ValueError('Incomplete execution')
    if meta['plan_sha256']!=canonical_hash(p) or meta['source_archive_sha256']!=p['source_archive_sha256']:
        raise ValueError('Wrong source plan')
    if len(jobs)!=22 or read('summary.json')!=summary(jobs):raise ValueError('Wrong complete summary')
    new=[]
    for actual,expected in zip(jobs,p['jobs']):
        if {k:v for k,v in actual.items() if k not in {'judgement','judge_provenance'}}!={k:v for k,v in expected.items() if k not in {'judgement','judge_provenance'}}:
            raise ValueError('Saved evidence changed')
        if expected['judgement'] is not None:
            if actual!=expected:raise ValueError('Transferred note changed')
        else:
            if actual['judge_provenance']!='new_judgement_21':raise ValueError('Wrong new provenance')
            new.append(actual)
        note=actual['judgement']
        if type(note['score']) is not int or not 1<=note['score']<=5 or not note['reason'].strip() or note.get('score_adjusted'):
            raise ValueError('Invalid raw note')
    raw_rows=[json.loads(s) for s in files['evaluation21_results/new_judgements.jsonl'].decode().splitlines()]
    if raw_rows!=[{'id':j['id'],'payload_sha256':j['payload_sha256'],'judgement':j['judgement']} for j in new]:
        raise ValueError('New note rows differ')
    events=[json.loads(s) for s in files['evaluation21_results/api_requests.jsonl'].decode().splitlines()]
    responses=[e for e in events if e['event']=='generation_response']
    if len(responses)!=8 or len(events)!=9:raise ValueError('Unexpected dispatch events')
    prior,_=financial_checkpoint();ledger_raw=files['evaluation21_results/budget_ledger_snapshot.json'];ledger=json.loads(ledger_raw)
    if hashlib.sha256(ledger_raw).hexdigest()!=meta['budget_ledger_snapshot_sha256']:raise ValueError('Ledger SHA differs')
    if any(ledger['requests'].get(k)!=v for k,v in prior['requests'].items()):raise ValueError('Previous reservations changed')
    if ledger['limit_usd']!='7.00' or len(ledger['requests'])!=175:raise ValueError('Wrong accounting ceiling/count')
    if set(ledger['requests'])-set(prior['requests'])!={e['request_id'] for e in responses}:raise ValueError('Accounting IDs differ')
    for event,job in zip(responses,new):
        parsed=json.loads(event['raw_final']);note=job['judgement']
        if parsed!={'puntaje':note['score'],'razon':note['reason']}:raise ValueError('Raw provider note differs')
        if event['protocol']!='ocr-evaluation-21' or event['free_project_attested'] is not False:raise ValueError('Wrong protocol')
        entry=ledger['requests'][event['request_id']]
        if entry['status']!='settled_from_verified_usage' or Decimal(entry['charged_or_reserved_usd'])!=Decimal(event['estimated_upper_cost_usd']):
            raise ValueError('Unverified settlement')
    total=sum(Decimal(e['charged_or_reserved_usd']) for e in ledger['requests'].values())
    if total!=Decimal(meta['estimated_or_reserved_total_usd']) or total>7:raise ValueError('Budget differs')
    human=receipt(root/'final/evidence/visual21_received/REVISION_VISUAL_21.md',root)
    humans={r['id']:r for r in human['reviews']}
    with zipfile.ZipFile(root/'final/evidence/integration20_completed/original_results.zip') as z:
        rows=[json.loads(s) for s in z.read('integration20_results/common_predictions.jsonl').decode().splitlines()]
    _,refs,_=load_common(root=root);details=[]
    for job,row,ref in zip(jobs,rows,refs):
        h=job['human_transfer'] or humans[job['id']]
        joined=join_row(ref,row['record'],job['judgement'],{'criteria':h['signed_criteria'],'observations':h['semantic_observations']})
        joined.update(id=job['id'],semantic_provenance=h.get('semantic_provenance'),judge_provenance=job['judge_provenance'])
        details.append(joined)
    passed=sum(d['domain_pass'] is True for d in details)
    return {'profile':PROFILE,'source_archive_sha256':ZIP_SHA,'source_commit':commit,'cases':22,
        'judge_mean_1_5':sum(j['judgement']['score'] for j in jobs)/22,
        'literal_fact_coverage_mean':sum(j['automatic']['literal_fact_coverage'] for j in jobs)/22,
        'domain_pass_count':passed,'domain_rate':passed/22,'domain_details':details,
        'judge_notes_reused':14,'judge_notes_new':8,'human_text_transfers':12,'human_visual_reviews':10,
        'prior_167_entries_unchanged':True,'estimated_or_reserved_total_usd':str(total),
        'incremental_estimated_usd':str(total-sum(Decimal(v['charged_or_reserved_usd']) for v in prior['requests'].values())),
        'actual_invoice_verified':False,'raw_scores_adjusted':False,'outputs_regenerated':False,
        'public_deployment_verified':False,'limitations':human['limitations']}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit()
    with args.output.open('x',encoding='utf-8') as out:json.dump(result,out,ensure_ascii=False,indent=2)
