"""Replay development contexts from preserved v5; not a retrieval/final benchmark."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def load_replay():
    archive=ROOT/'evidence/integration_v5/contractrisk_m3_integracion_v5_resultados.zip'
    with zipfile.ZipFile(archive) as z:
        rows=[json.loads(line) for line in z.read('predictions.jsonl').splitlines()]
    if len(rows)!=32 or len({(r['variant'],r['development_index']) for r in rows})!=32:
        raise ValueError('Expected preserved 32 development rows')
    return rows,hashlib.sha256(archive.read_bytes()).hexdigest()


class FrozenRetriever:
    def __init__(self, question, contexts):
        self.question,self.contexts=question,contexts

    def search(self, question, top_k):
        if question!=self.question:
            raise ValueError('Replay question mismatch')
        return list(self.contexts[:top_k])


def run_replay(generator, tools, emit):
    from correction_v6 import generate_v6, ROUTER_V6
    from agent_v5 import CandidateAgent
    rows,_=load_replay()
    for old in rows:
        question=old['question']; start=time.perf_counter()
        if old['variant']=='agent_v5':
            retriever=FrozenRetriever(question,old['retrieved_contexts'])
            result=CandidateAgent(retriever,generator,tools,router_system=ROUTER_V6,
                                  answer_fn=generate_v6).predict(question)
        else:
            result=generate_v6(generator,question,old['contexts'])
            result.update(question=question,contexts=old['contexts'],latency_seconds=time.perf_counter()-start)
        # Diagnostic expectations remain outside all model calls.
        result.update(variant=old['variant'].replace('_v5','_v6_replay'),
                      development_index=old['development_index'],review_only=old['review_only'],
                      replay_contexts=True,latency_not_comparable_to_live_retrieval=True)
        emit(result)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Choose a NEW output directory; do not overwrite evidence')
    args.output.mkdir(parents=True)
    meta={'status':'started','purpose':'development_context_replay_and_judge_calibration_NOT_final',
          'started_utc':datetime.now(timezone.utc).isoformat(),'seed':42,'python':platform.python_version(),
          'quality_status':'requires_semantic_review','rebuilds_retrieval':False}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        import torch
        import numpy as np
        from response_v4 import TrackedGenerator
        from systems_v5 import GENERATOR_ID,GENERATOR_REVISION
        from correction_v6 import ANSWER_V6,ROUTER_V6,JUDGE_V6,ContrastJudge
        from calibration_v1 import evaluate_calibration,summarize_calibration,calibration_cases
        from contract_tools import ContractTools
        if not torch.cuda.is_available():
            raise RuntimeError('Enable T4 GPU before running')
        random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42)
        _,replay_sha=load_replay()
        meta.update(gpu=torch.cuda.get_device_name(0),model=GENERATOR_ID,revision=GENERATOR_REVISION,
                    judge_same_model=True,replay_zip_sha256=replay_sha,
                    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},
                    prompt_hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in
                                   [('answer',ANSWER_V6),('router',ROUTER_V6),('judge',JUDGE_V6)]},
                    packages={p:importlib.metadata.version(p) for p in ['torch','transformers','numpy']})
        save()
        docs=[json.loads(line) for line in (ROOT/'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        start=time.perf_counter()
        generator=TrackedGenerator(GENERATOR_ID,GENERATOR_REVISION,max_new_tokens=512)
        meta['loading_seconds']=time.perf_counter()-start;save()
        with (args.output/'predictions.jsonl').open('w',encoding='utf-8') as out:
            def emit(row):
                print(row['variant'],row['development_index'],flush=True)
                out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
            run_replay(generator,ContractTools(docs),emit)
        (args.output/'calibration_cases.json').write_text(json.dumps(calibration_cases(),ensure_ascii=False,indent=2),encoding='utf-8')
        with (args.output/'calibration.jsonl').open('w',encoding='utf-8') as out:
            def emit_judge(row):
                print(row['condition'],row['case_id'],row['length'],flush=True)
                out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
            rows=evaluate_calibration(generator,emit_judge,judge_factory=ContrastJudge)
        summary=summarize_calibration(rows)
        (args.output/'calibration_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        meta.update(status='completed',judge_quote_mismatches=sum(r['judgement']['quoted_answer_matches'] is False for r in rows),
                    max_gpu_allocated_bytes=torch.cuda.max_memory_allocated())
    except Exception as exc:
        meta.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
    finally:
        meta['finished_utc']=datetime.now(timezone.utc).isoformat();save()


if __name__=='__main__':
    main()
