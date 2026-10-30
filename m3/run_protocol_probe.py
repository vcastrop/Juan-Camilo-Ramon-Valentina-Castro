"""Small synthetic A/B protocol and model comparison, no final gold access."""
import argparse
import gc
import hashlib
import importlib.metadata
import json
import platform
import random
import statistics
import time
import traceback
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output folder to preserve evidence')
    args.output.mkdir(parents=True)
    meta={'purpose':'synthetic_protocol_probe_not_final_evaluation','status':'started',
          'started_utc':datetime.now(timezone.utc).isoformat(),'seed':42,
          'python':platform.python_version(),'max_new_tokens':512,'arms':[]}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        import torch
        import numpy as np
        from response_v4 import TrackedGenerator,SYSTEM_V4
        from agent_v4 import CONTROLLER_V4
        from protocol_probe import probe_cases,run_answer,run_route,check_response,ANSWER_V5,ROUTER_V5
        assert torch.cuda.is_available(),'Activate a GPU T4'
        random.seed(42); np.random.seed(42); torch.manual_seed(42); torch.cuda.manual_seed_all(42)
        meta.update(gpu=torch.cuda.get_device_name(0),
                    packages={p:importlib.metadata.version(p) for p in ['torch','transformers','numpy','huggingface-hub']},
                    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},
                    prompt_hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in
                                   {'answer_v4':SYSTEM_V4,'route_v4':CONTROLLER_V4,'answer_v5':ANSWER_V5,'route_v5':ROUTER_V5}.items()})
        answers,routes=probe_cases()
        cases={'synthetic':True,'answers':answers,'routing':routes}
        cases_text=json.dumps(cases,ensure_ascii=False,indent=2)+'\n'
        (args.output/'cases.json').write_text(cases_text,encoding='utf-8')
        meta['cases_sha256']=hashlib.sha256(cases_text.encode()).hexdigest()
        models=[('Qwen/Qwen2.5-1.5B-Instruct','989aa7980e4cf806f80c7fef2b1adb7bc71aa306',['v4','v5']),
                ('Qwen/Qwen2.5-3B-Instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1',['v5'])]
        summaries=[]
        with (args.output/'predictions.jsonl').open('w',encoding='utf-8') as output:
            for name,revision,protocols in models:
                generator=None
                model_start=time.perf_counter()
                try:
                    arm_info={'model':name,'revision':revision,'protocols':protocols,'status':'loading'}
                    meta['arms'].append(arm_info); save()
                    print(f'Loading {name} revision {revision}',flush=True)
                    torch.cuda.reset_peak_memory_stats()
                    generator=TrackedGenerator(name,revision,max_new_tokens=512)
                    arm_info['loading_seconds']=time.perf_counter()-model_start
                    for protocol in protocols:
                        records=[]
                        for kind,items in [('answer',answers),('routing',routes)]:
                            for case in items:
                                print(f'{name} / {protocol} / {case["id"]}',flush=True)
                                start=time.perf_counter()
                                record={'model':name,'revision':revision,'protocol':protocol,
                                        'case_id':case['id'],'kind':kind}
                                try:
                                    result=run_answer(generator,case,protocol) if kind=='answer' else run_route(generator,case,protocol)
                                    record['result']=result
                                    if kind=='answer':
                                        record['checks']=check_response(case,result['output'])
                                    record['error']=None
                                except Exception as exc:
                                    record.update(result=None,error=f'{type(exc).__name__}: {exc}')
                                record['latency_seconds']=time.perf_counter()-start
                                output.write(json.dumps(record,ensure_ascii=False)+'\n'); output.flush()
                                records.append(record)
                        answer_rows=[r for r in records if r['kind']=='answer']
                        routing_rows=[r for r in records if r['kind']=='routing']
                        summaries.append({'model':name,'revision':revision,'protocol':protocol,
                            'total_cases':len(records),'execution_errors':sum(r['error'] is not None for r in records),
                            'answer_total':len(answer_rows),
                            'answer_first_valid':sum(bool(r['result'] and r['result']['first_attempt_valid']) for r in answer_rows),
                            'answer_final_valid':sum(bool(r['result'] and r['result']['output'] is not None) for r in answer_rows),
                            'answer_mechanical_pass':sum(bool(r.get('checks',{}).get('mechanical_pass')) for r in answer_rows),
                            'routing_total':len(routing_rows),
                            'routing_correct':sum(bool(r['result'] and r['result']['selection_correct']) for r in routing_rows),
                            'median_seconds':statistics.median(r['latency_seconds'] for r in records),
                            'semantic_review_required':True})
                        (args.output/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8')
                    arm_info['status']='completed'
                    arm_info['peak_allocated_gpu_bytes']=torch.cuda.max_memory_allocated()
                except Exception as exc:
                    meta.setdefault('model_errors',[]).append({'model':name,'revision':revision,'error':f'{type(exc).__name__}: {exc}'})
                    if meta['arms'] and meta['arms'][-1]['model']==name:
                        meta['arms'][-1]['status']='failed'
                    (args.output/(name.split('/')[-1]+'_error.txt')).write_text(traceback.format_exc(),encoding='utf-8')
                    print(f'Model failed; retained diagnostics: {exc}',flush=True)
                finally:
                    del generator
                    gc.collect(); torch.cuda.empty_cache()
                    save()
        meta['status']='completed_with_errors' if meta.get('model_errors') or any(s['execution_errors'] for s in summaries) else 'completed'
    except Exception as exc:
        meta.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        meta['finished_utc']=datetime.now(timezone.utc).isoformat()
        save()


if __name__=='__main__':
    main()
