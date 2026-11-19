"""Recalculate stored comparison diagnostics and tool usage, without inference or remote writes."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from final.common_harness import load_common,evaluate,valid_output
from final.collection_profiles import PROFILES
from final.prepare_eval_final import canonical_hash
from final.tool_usage import summarize

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE_SHA256='34a5b0616c77b790489d3ecf37469cf312a0de6ea950ce39a193b72027c22de9'


def audit(archive=None):
    archive=Path(archive or ROOT/'final/evidence/comparison_02/original_results.zip')
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=ARCHIVE_SHA256:raise ValueError('Comparison evidence changed')
    inputs,refs,pack=load_common();tables=[];tools={};observations={}
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Corrupt comparison archive')
        meta=json.loads(z.read('metadata.json'))
        if meta['git_commit']!='8cbeb36ebdf3dde472920ffd7a655c0a5c5af38e' or meta['profiles_completed']!=PROFILES:raise ValueError('Incomplete or unexpected collection')
        if meta['inputs_sha256']!=pack['inputs_canonical_sha256'] or meta['references_sha256']!=pack['references_canonical_sha256']:raise ValueError('Common package changed')
        for profile in PROFILES:
            rows=[json.loads(s) for s in z.read(profile+'/predictions.jsonl').decode().splitlines()]
            if [r['id'] for r in rows]!=[i['id'] for i in inputs]:raise ValueError('Case IDs/order changed')
            details,summary=evaluate(rows,refs,judge=None)
            saved=json.loads(z.read(profile+'/scorecard_candidate.json'))
            if canonical_hash(details)!=canonical_hash(json.loads(z.read(profile+'/automatic_details.json'))):raise ValueError('Per-case diagnostic mismatch')
            for key,value in summary.items():
                if value!=saved[key]:raise ValueError('Diagnostic mismatch: '+profile+'/'+key)
            tools[profile]=summarize(rows);observations[profile]={r['id']:r['record'] for r in rows}
            tables.append({'profile':profile,'cases':len(rows),'valid_schema':sum(valid_output(r['record'].get('output')) for r in rows),
                'literal_coverage_mean':summary['literal_fact_coverage_mean'],'automatic_checks_rate':summary['automatic_checks_rate'],
                'p50_seconds':summary['wall_p50_seconds'],'p95_seconds':summary['wall_p95_seconds'],
                'peak_cuda_allocated_bytes':max(r['peak_cuda_allocated_bytes'] for r in rows),
                'judge_mean':None,'domain_rate':None})
    before=next(t for t in tables if t['profile']=='integrated_fp16');after=next(t for t in tables if t['profile']=='integrated_nf4')
    return {'archive_sha256':ARCHIVE_SHA256,'collection_commit':meta['git_commit'],'tables':tables,
        'corrected_tool_usage':tools,'original_wandb_series_rewritten':False,
        'memory_reduction_fraction':1-after['peak_cuda_allocated_bytes']/before['peak_cuda_allocated_bytes'],
        'median_latency_change_fraction':after['p50_seconds']/before['p50_seconds']-1,
        'visual_extractions_identical':all(observations['integrated_fp16'][i['id']].get('visual',{}).get('output')==
            observations['integrated_nf4'][i['id']].get('visual',{}).get('output') for i in inputs if i['image']),
        'ablation_changed_outputs':[i['id'] for i in inputs if observations['integrated_fp16'][i['id']].get('output')!=observations['integrated_no_tool_fp16'][i['id']].get('output')],
        'judge_validated':False,'efficiency_status':'not_evaluable_pending_validated_judge_and_semantic_audit',
        'deployment_decision':'NF4 not accepted for deployment; FP16 is only a development baseline, not globally validated quality.'}


if __name__=='__main__':
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
