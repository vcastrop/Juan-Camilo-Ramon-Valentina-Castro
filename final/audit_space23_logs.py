"""Audit user-provided public service logs offline; never infer W&B crash causes."""
import hashlib
import json
from pathlib import Path

from final.service_contract import validate_event

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=['99daad02-dec8-497a-b6f2-7bb359dc6b7e','f39ccd4c-ffdd-4c32-aad7-a0e0c4c4decb',
          'd96c6779-5469-4607-b1fa-82df52e8d96f','40b758fc-d5a8-4b32-8b5d-91791487927e',
          'a30200cc-7661-47d4-8f49-5e671e26caf8','84603007-a660-4427-a448-0b05b3be0e7b',
          'b496f6bd-e569-45a0-a738-41822e2f46a8']


def audit(path):
    raw=Path(path).read_bytes();text=raw.decode('utf-8-sig')
    events=[];blocks=[]
    for line in text.splitlines():
        if line.startswith('{'):
            item=json.loads(line)
            if item.get('event_type')=='contract_request':
                validate_event(item);events.append(item);blocks.append([])
        elif blocks:blocks[-1].append(line)
    if len(events)!=10 or len({e['request_id'] for e in events})!=10:raise ValueError('Expected ten distinct events')
    if any(e['version']!='5b42adc35d6e3225c93dfbda13ae2e1730bad1c8' for e in events):raise ValueError('Wrong service version')
    accepted=[e for e in events if e['success']]
    if [e['request_id'] for e in accepted]!=EXPECTED:raise ValueError('Smoke evidence differs')
    rejected=[]
    for event,block in zip(events,blocks):
        if event['success']:continue
        if event['error_code']!='invalid_input' or event['components_known'] or event['latency_seconds']!=0:
            raise ValueError('Unexpected runtime failure, investigate')
        transcript='\n'.join(block)
        if "Confirma el aviso de uso y privacidad antes de consultar." in transcript:reason='consent_missing'
        elif "Introduce una descripción o una imagen con objeto legible." in transcript:reason='m1_description_and_image_missing'
        else:raise ValueError('Unclassified rejection')
        rejected.append({'request_id':event['request_id'],'reason':reason})
    if [r['reason'] for r in rejected]!=['consent_missing','consent_missing','m1_description_and_image_missing']:
        raise ValueError('Rejection sequence differs')
    return {'source_log_sha256':hashlib.sha256(raw).hexdigest(),'events':events,'total_events':10,
            'accepted_smoke_events':7,'rejected_input_events':3,'runtime_error_events':0,
            'rejection_reasons':rejected,'valid_requests_successful':7,
            'raw_success_fraction_all_attempts':0.7,'fraction_is_not_quality_accuracy':True,
            'wandb_run':'f7ljlxip','wandb_crashed_reported':True,'wandb_crash_cause':None,
            'space_health_after_crash':'ready_true_real_request_verified_true_user_reported',
            'monitoring_live_connection_verified':False,'independent_external_access_verified':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('log',type=Path);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();result=audit(a.log)
    with a.output.open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False,indent=2)
