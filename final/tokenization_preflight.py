"""Tokenizer-only checks against the original Mistral messages; no model weights/GPU."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from final.chat_encoding import encode_chat
from final.calibration_final import cases,schedule,verbose
from final.judge_final import FinalJudge
from final.prepare_eval_final import canonical_hash
from judge import evidence_payload


def check_inputs(tokenizer,reference_rows):
    old={(r['condition'],r['id']):r for r in reference_rows}
    if len(old)!=38 or set(old)!=set(schedule()):raise ValueError('Unexpected reference schedule')
    by_id={c['id']:c for c in cases()};rows=[]
    for condition,cid in schedule():
        record=by_id[cid]['record']
        if condition.endswith('verbose'):record=verbose(record)
        system=FinalJudge(None,mitigate_verbosity=not condition.startswith('before_')).system
        user=json.dumps(evidence_payload(record),ensure_ascii=False)
        messages=[{'role':'system','content':system},{'role':'user','content':user}]
        rendered=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        legacy=tokenizer(rendered)['input_ids']
        encoded,audit=encode_chat(tokenizer,system,user)
        corrected=encoded['input_ids']
        original_count=old[(condition,cid)]['judgement']['attempts'][0]['generation']['input_tokens']
        rows.append({'condition':condition,'id':cid,'legacy_length':len(legacy),'original_length':original_count,
                     'legacy_length_matches_reference':len(legacy)==original_count,
                     'one_extra_bos_reproduced':legacy==[tokenizer.bos_token_id]+corrected,
                     'corrected_native_equivalent':audit['native_equivalent'],
                     'corrected_length':len(corrected),'corrected_prefix':corrected[:4],'encoding':audit})
    counts={'legacy_lengths_match':sum(r['legacy_length_matches_reference'] for r in rows),
            'one_extra_bos_reproduced':sum(r['one_extra_bos_reproduced'] for r in rows),
            'corrected_native_matches':sum(r['corrected_native_equivalent'] for r in rows)}
    return {'passed':all(value==38 for value in counts.values()),'cases':38,**counts,'rows':rows}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cache-dir',type=Path)
    p.add_argument('--local-files-only',action='store_true')
    args=p.parse_args()
    if args.output.exists():p.error('Do not overwrite a tokenization preflight')
    from final.run_mistral_tokenfix import verify_reference
    comparison=verify_reference()
    config=json.loads((ROOT/'final/judge_second_config.json').read_text(encoding='utf-8'))
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['revision'],trust_remote_code=False,
                                          cache_dir=str(args.cache_dir) if args.cache_dir else None,local_files_only=args.local_files_only)
    with zipfile.ZipFile(ROOT/'final/evidence/judge02_legacy/original_results.zip') as z:
        old=[json.loads(s) for s in z.read('raw_judgements.jsonl').decode().splitlines()]
    report=check_inputs(tokenizer,old)
    report.update(model=config['model'],revision=config['revision'],model_inference_performed=False,gpu_used=False,
                  reference_archive_sha256=comparison['reference_archive_sha256'],config_canonical_sha256=canonical_hash(config),
                  source_sha256={name:hashlib.sha256((ROOT/'final'/name).read_bytes()).hexdigest()
                                 for name in ['chat_encoding.py','tokenization_preflight.py','judge_final.py','calibration_final.py']},
                  packages={n:importlib.metadata.version(n) for n in ['transformers','tokenizers','huggingface-hub']})
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
    if not report['passed']:raise RuntimeError('Tokenizer preflight failed; do not load model')


if __name__=='__main__':main()
