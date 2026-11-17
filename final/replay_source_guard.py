"""Post-hoc CPU orchestration replay, never new model inference or blind evaluation."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
from final.integration import IntegratedSystem
from final.config import VERSION


def run(output):
    if output.exists():
        raise FileExistsError('Use a new output directory')
    archive=ROOT/'final/evidence/visual_03/original_results.zip'
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest!='726b612ae3a09be703cfa2ab3609d2ef90ca3b1de208a1dd2298980e34931d00':
        raise ValueError('Historical archive changed')
    corpus=ROOT/'m3/corpus/documents.jsonl'
    if hashlib.sha256(corpus.read_bytes()).hexdigest()!='7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505':
        raise ValueError('Corpus changed')
    docs=[json.loads(s) for s in corpus.read_text(encoding='utf-8').splitlines()]
    with zipfile.ZipFile(archive) as z:
        rows=[json.loads(s) for s in z.read('predictions.jsonl').decode().splitlines()]
        cases={c['id']:c for c in json.loads(z.read('reviewed_visual_pack/manifest.json'))}
    output.mkdir(parents=True)
    replay=[]
    for row in rows:
        original=row['result']
        class SavedVision:
            def extract(self,image):
                return copy.deepcopy(original['visual'])
        uses=[]
        def saved_answer(question,visual_context):
            uses.append(True)
            return copy.deepcopy({k:original[k] for k in ['output','contexts','tool_trace','tool_calls','parse_error'] if k in original})
        result=IntegratedSystem(docs,saved_answer,vision=SavedVision()).predict(cases[row['id']]['question'],image=object())
        replay.append({'id':row['id'],'old_output':original['output'],'new_orchestration':result,
                       'saved_answer_callback_used':bool(uses),'model_inference_performed':False,
                       'output_changed':original['output']!=result['output']})
    (output/'replay_rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in replay),encoding='utf-8')
    meta={'purpose':'post_hoc_cpu_replay_of_saved_readings_not_new_inference', 'version':VERSION,
          'created_utc':datetime.now(timezone.utc).isoformat(),'archive_sha256':digest,
          'case_count':len(replay),'model_inference_performed':False,'quality_approved':False,
          'blocked_ids':[r['id'] for r in replay if r['new_orchestration']['guard']=='visual_source_conflict'],
          'output_changed_ids':[r['id'] for r in replay if r['output_changed']],
          'warning':'A refusal to confirm a readable amount prevents propagation but does not repair OCR or make the original expected answer correct. No final scorecard improvement claimed.'}
    (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return meta


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(run(args.output),ensure_ascii=False,indent=2))
