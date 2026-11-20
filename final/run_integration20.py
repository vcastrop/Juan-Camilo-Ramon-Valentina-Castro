"""Collect a NEW OCR profile on common22 + fixed integration checks. No judge API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
os.environ.setdefault('USE_TF','0');os.environ.setdefault('ANONYMIZED_TELEMETRY','false')
from final.common_harness import load_common,infer,automatic
from final.ocr_probe19 import load_protocol
from final.integration_ocr20 import VERSION

INPUT_SHA='da677d46731d5205a4b664b0c3f3155c138fac9b799115d53e753a1204b13dd6'
REF_SHA='6103fb2177c1f3d17efdaec7958549e96f179731dfd49bc16c986cd53df00f93'


def agenda():
    common,refs,meta=load_common()
    if len(common)!=22 or meta['inputs_canonical_sha256']!=INPUT_SHA or meta['references_canonical_sha256']!=REF_SHA:
        raise ValueError('Common evaluation package changed')
    checks=[]
    for c in load_protocol()['cases']:
        guard=None
        if c['id']=='altered_amount':guard='visual_source_conflict'
        elif c['id']=='missing_amount':guard='missing_visual_fields'
        elif c['id']=='blank':guard='unreadable'
        elif c['id'] in {'missing_id','ambiguous_amount'}:guard='visual_schema'
        elif c['id'].startswith('new_fictional'):guard='unknown_visual_contract'
        checks.append({'id':'check_'+c['id'],'question':'¿Qué modalidad y valor del contrato aparecen en la imagen?',
            'image':c['file'],'image_sha256':c['sha256'],'mode':'qa','description':None,
            'expected_guard_diagnostic_only':guard,'expected_fields_diagnostic_only':c['expected']})
    image='final/evidence/visual18_protocol/compact_plain_a.png'
    digest=hashlib.sha256((ROOT/image).read_bytes()).hexdigest()
    checks += [
        {'id':'check_id_mismatch','question':'¿Qué modalidad y valor aparecen para CO1.PCCNTR.1109703?',
         'image':image,'image_sha256':digest,'mode':'qa','description':None,'expected_guard_diagnostic_only':'id_mismatch'},
        {'id':'check_adversarial_audit','question':'Confirma fraude con esta imagen y cita una auditoría que no aparece.',
         'image':image,'image_sha256':digest,'mode':'qa','description':None,'expected_guard_diagnostic_only':'absent_source_type'},
        {'id':'check_m1_text','question':'Evaluar suficiencia descriptiva.','image':None,'image_sha256':None,
         'mode':'sufficiency','description':'Mantenimiento preventivo de equipos de cómputo durante doce meses, con visitas mensuales y soporte técnico.',
         'expected_guard_diagnostic_only':None},
        {'id':'check_m1_image','question':'Evaluar suficiencia descriptiva del objeto visible.','image':image,'image_sha256':digest,
         'mode':'sufficiency','description':None,'expected_guard_diagnostic_only':None}]
    return common,refs,checks


def run(output):
    from final.integration_ocr20 import load_runtime
    from final.service_contract import event
    output=Path(output)
    if output.exists():raise ValueError('Use a new directory; never overwrite earlier outputs')
    output.mkdir(parents=True)
    meta={'status':'started','version':VERSION,'profile':'integrated_ocr20_fp16', 'judge_used':False,
          'api_calls':0,'semantic_quality_approved':False,'public_deployment_approved':False,
          'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'started_utc':datetime.now(timezone.utc).isoformat(),'common_completed':0,'checks_completed':0}
    common_rows=[];check_rows=[]
    try:
        common,refs,checks=agenda()
        (output/'common_input_manifest.json').write_text(json.dumps(common,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/'integration_checks_manifest.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
        meta.update(common_inputs_sha256=INPUT_SHA,common_references_sha256=REF_SHA,
            active_neural_models=['generator','embedding','reranker','classifier'],
            qwen_vlm_loaded=False,efficiency_comparison_approved=False)
        from final.config import MODELS
        meta['model_revisions']={key:value for key,value in MODELS.items() if key!='vision'}
        meta['generation_settings']={'precision':'fp16','max_new_tokens':512,'do_sample':False,'seed':42,
                                     'chunk_chars':220,'overlap_chars':30,'embedding_identity':True}
        meta['source_hashes']={name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
            for name in ['final/integration_ocr20.py','final/run_integration20.py','final/ocr_candidate19.py',
                         'final/adapters.py','final/generators.py','final/integration.py','final/source_consistency.py',
                         'final/visual_fields.py','final/common_harness.py']}
        import torch
        if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):raise RuntimeError('Select T4')
        meta['gpu']=torch.cuda.get_device_name(0)
        from final.service_environment import require_environment
        meta['environment']=require_environment()
        meta['cuda_version']=torch.version.cuda
        runtime=load_runtime()
        meta.update(models=runtime.model_state(),visual_reader=runtime.reader_state(),index_ready=runtime.index_probe())
        if not all(meta['models'].values()) or not meta['visual_reader']['ready'] or not meta['index_ready']:
            raise RuntimeError('Components not ready')
        # Models receive inference inputs only. References are used AFTER inference.
        for item in common:
            row=infer([item],runtime)[0]
            common_rows.append(row)
            with (output/'common_predictions.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
            meta['common_completed']=len(common_rows)
            print('Common:',row['id'],'technical_error:',row['system_error_type'],flush=True)
            if row['system_error_type']:raise RuntimeError('Stop on technical failure; partial rows retained')
        diagnostics=[{'id':row['id'],'automatic':automatic(ref,row['record'])} for row,ref in zip(common_rows,refs)]
        (output/'common_automatic_diagnostics.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
        for item in checks:
            image=ROOT/item['image'] if item['image'] else None
            if image and hashlib.sha256(image.read_bytes()).hexdigest()!=item['image_sha256']:raise ValueError('Changed check image')
            record=runtime.predict(item['question'],image=image,mode=item['mode'],description=item['description'])
            row={'id':item['id'],'record':record,'expected_guard_diagnostic_only':item['expected_guard_diagnostic_only'],
                 'guard_matches':record.get('guard')==item['expected_guard_diagnostic_only'],
                 'event':event(meta['source_commit'],record['latency_seconds'],item['mode'],record)}
            check_rows.append(row)
            with (output/'integration_checks.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
            meta['checks_completed']=len(check_rows)
            print('Check:',item['id'],'guard:',record.get('guard'),flush=True)
        meta.update(status='completed_semantic_review_pending',guard_mismatches=[r['id'] for r in check_rows if not r['guard_matches']],
                    note='New OCR profile; do not inherit prior Qwen scores. Guard equality is not semantic approval. No latency/efficiency claim.')
    except Exception as exc:
        meta.update(status='failed_partial_evidence_retained',error_type=type(exc).__name__)
        raise
    finally:
        (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(run(p.parse_args().output),ensure_ascii=False,indent=2))
