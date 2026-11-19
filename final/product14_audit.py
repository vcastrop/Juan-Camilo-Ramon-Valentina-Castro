"""Offline verification of the 110 real judge notes and cumulative USD 7 accounting."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

from final.api_budget7 import AUTHORIZATION
from final.human_closure_receipt import receive_closure
from final.paid_transition_preflight import read_archive
from final.product_judge14 import product_plan
from final.run_product_judge14 import summary

ZIP_SHA = '410a155249fa1e3e5d754324a3e94e1506ea2806ec53c3cf4e7fffdcd2a56c3f'
NB_SHA = '3dc54c426ca80016933cd2b9a10f17418594e8da89d8ecf0995941c231f89099'


def audit(root):
    root = Path(root)
    files = read_archive(root/'final/evidence/product_14/original_results.zip', ZIP_SHA)
    meta = json.loads(files['metadata.json'])
    rows = [json.loads(s) for s in files['raw_judgements.jsonl'].decode().splitlines()]
    jobs = json.loads(files['execution_manifest.json'])
    expected = product_plan(root)['jobs']
    if len(rows) != 110 or len(jobs) != 110 or not summary(jobs)['complete']:
        raise ValueError('Incomplete product evaluation')
    if summary(jobs) != json.loads(files['judge_summary.json']):
        raise ValueError('Judge summary differs')
    for actual, intended, row in zip(jobs, expected, rows):
        for key in ['profile', 'id', 'source_record_sha256', 'judge_payload', 'payload_sha256']:
            if actual[key] != intended[key]:
                raise ValueError('Saved system evidence changed')
        if row['profile'] != actual['profile'] or row['id'] != actual['id'] or row['judgement'] != actual['judgement']:
            raise ValueError('Judge row differs from execution manifest')
    if meta['status'] != 'completed_110_judgements_audit_pending' or meta['generation_http_calls'] != 110:
        raise ValueError('Unexpected execution status')
    if meta['authorization'] != AUTHORIZATION:
        raise ValueError('Total authorization differs')
    for name, expected_hash in meta['source_hashes'].items():
        data = subprocess.check_output(['git', 'show', meta['git_commit']+':'+name], cwd=root)
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise ValueError('Execution source hash differs')
    events = [json.loads(s) for s in files['api_requests.jsonl'].decode().splitlines()]
    responses = [e for e in events if e['event'] == 'generation_response']
    if len(responses) != 110 or any(e['event'] not in {'generation_response', 'model_preflight'} for e in events):
        raise ValueError('Unexpected API events')
    for response, row in zip(responses, rows):
        note = json.loads(response['raw_final'])
        if note['puntaje'] != row['judgement']['score'] or note['razon'] != row['judgement']['reason']:
            raise ValueError('Raw note changed')
        if response.get('free_project_attested') is not False:
            raise ValueError('Incorrect free-project attestation')
    raw = files['budget_ledger_snapshot.json']
    if hashlib.sha256(raw).hexdigest() != meta['budget_ledger_snapshot_sha256']:
        raise ValueError('Budget hash differs')
    ledger = json.loads(raw)
    from final.confirmation13_receipt import SHA13
    previous = read_archive(root/'final/evidence/confirmation_13/original_results.zip', SHA13)
    if files['api_budget_ledger_before_usd7.json'] != previous['budget_ledger_snapshot.json']:
        raise ValueError('USD 5 backup differs from confirmation13')
    prior = json.loads(previous['budget_ledger_snapshot.json'])
    for key, value in prior['requests'].items():
        if ledger['requests'].get(key) != value:
            raise ValueError('Historical reservation changed')
    new = set(ledger['requests'])-set(prior['requests'])
    if len(new) != 110 or new != {e['request_id'] for e in responses} or ledger['limit_usd'] != '7.00':
        raise ValueError('Accounting IDs or ceiling differ')
    for event in responses:
        row = ledger['requests'][event['request_id']]
        if row['status'] != 'settled_from_verified_usage' or Decimal(row['charged_or_reserved_usd']) != Decimal(event['estimated_upper_cost_usd']):
            raise ValueError('Usage accounting differs')
    total = sum(Decimal(r['charged_or_reserved_usd']) for r in ledger['requests'].values())
    if total != Decimal('5.7954525') or total != Decimal(meta['estimated_or_reserved_total_usd']):
        raise ValueError('Unexpected cumulative budget')
    nb_raw = (root/'final/evidence/product_14/executed.ipynb').read_bytes()
    if hashlib.sha256(nb_raw).hexdigest() != NB_SHA:
        raise ValueError('Executed notebook changed')
    nb = json.loads(nb_raw)
    reference = json.loads(subprocess.check_output(['git', 'show', meta['git_commit']+':final/ContractRisk_Final_Evaluacion_14_Colab.ipynb'], cwd=root))
    source = lambda c: ''.join(c['source']).strip()
    expected_code = [source(c) for c in reference['cells'] if c['cell_type'] == 'code']
    executed_code = [source(c) for c in nb['cells'] if c['cell_type'] == 'code' and c.get('execution_count') is not None]
    if executed_code != expected_code:
        raise ValueError('Executed code differs')
    extras = [c for c in nb['cells'] if c['cell_type'] == 'code' and c.get('execution_count') is None and source(c)]
    allowed_extra_output = lambda o: (o.get('output_type') == 'stream' and o.get('name') == 'stdout'
                                      and ''.join(o.get('text', [])).strip() == 'Mounted at /content/drive')
    if (len(extras) != 1 or source(extras[0]) != expected_code[2]
            or not all(allowed_extra_output(o) for o in extras[0].get('outputs', []))):
        raise ValueError('Unexpected unexecuted notebook code')
    if any(o.get('output_type') == 'error' for c in nb['cells'] for o in c.get('outputs', [])):
        raise ValueError('Notebook contains errors')
    return {'version': 'product14-offline-audit-1', 'product_rows': rows, 'jobs': jobs,
            'judge_summary': summary(jobs), 'source_hashes_verified': len(meta['source_hashes']),
            'notebook_note': 'One duplicated read-only preflight cell has no execution count and only a Drive mount message; do not infer it never started. Six numbered cells match the published code; accounting proves 110 generation dispatches, not a duplicated paid run.',
            'cumulative_estimated_or_reserved_usd': str(total),
            'new_conservative_estimate_usd': str(sum(Decimal(ledger['requests'][k]['charged_or_reserved_usd']) for k in new)),
            'remaining_local_margin_usd': str(Decimal(7)-total), 'actual_invoice_verified': False,
            'originals_changed': False, 'network_requests_made_by_audit': 0,
            'human_closure': receive_closure(root)}
