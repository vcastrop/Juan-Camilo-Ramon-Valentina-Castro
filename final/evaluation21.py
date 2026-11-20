"""Offline provenance/equivalence and unsigned human review of the NEW OCR profile."""
import base64
import copy
import hashlib
import html
import json
from pathlib import Path
import subprocess
import zipfile

from final.common_harness import load_common,automatic
from final.prepare_eval_final import canonical_hash
from final.judge_final import rubric_fingerprint
from m3.judge import evidence_payload

ROOT=Path(__file__).resolve().parents[1]
SHA20='af18c90271ec3561057644f672f9619d064ce6a135dd6bb6c21cc68a2b17db21'
NB20='567a1d43a95a02c4f46bf9b2b2d393503488ce34dad44dbfa681bb303b4323bb'
# SHA of the committed LF bytes, independent of Windows checkout CRLF conversion.
DOMAIN_SHA='9d0234e0aaf546414a80b594fc4165586194b12cbcd54b4f812012ca1fc9ff6d'
PROFILE='integrated_ocr20_fp16'
CRITERIA=['Respuesta respaldada','Explicación respaldada y no vacía','Completa para lo preguntado',
          'Citas respaldan lo afirmado','Abstención adecuada','Fallos críticos']


def verify_domain_bytes(raw):
    # Normalize only CRLF, not JSON values, spaces, ordering or other content.
    if hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()!=DOMAIN_SHA:
        raise ValueError('Signed domain closure differs')


def make_jobs(rows,old,notes,refs,humans):
    jobs=[]
    for row,ref in zip(rows,refs):
        cid=row['id']
        if cid!=ref['id'] or row.get('system_error_type'):raise ValueError('Incomplete or reordered responses')
        payload=evidence_payload(row['record']);digest=canonical_hash(payload)
        prior=old[cid]
        same=payload==evidence_payload(prior['record'])
        judgement=copy.deepcopy(notes[cid]) if same else None
        human=copy.deepcopy(humans[cid]) if same and ref['input_modality']=='text' else None
        jobs.append({'profile':PROFILE,'id':cid,'source_record_sha256':canonical_hash(row),
            'judge_payload':payload,'payload_sha256':digest,'judgement':judgement,
            'judge_provenance':'exact_packet_transfer_product14' if same else 'pending_new_evaluation',
            'source_judge_key':'integrated_fp16/'+cid if same else None,
            'human_transfer':human,'human_provenance':'exact_text_packet_transfer_signed_review' if human else 'pending_new_visual_review',
            'new_human_review_claimed':False,'automatic':automatic(ref,row['record'])})
    return jobs


def plan(root=ROOT):
    from final.product14_audit import audit as audit14
    from final.prepare_product_judge_plan import COMPARISON_SHA
    from final.paid_transition_preflight import read_archive
    root=Path(root)
    archive=root/'final/evidence/integration20_completed/original_results.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA20:raise ValueError('Changed integration20 archive')
    if hashlib.sha256((archive.parent/'executed.ipynb').read_bytes()).hexdigest()!=NB20:raise ValueError('Changed executed notebook20')
    with zipfile.ZipFile(archive) as z:
        meta=json.loads(z.read('integration20_results/metadata.json'))
        rows=[json.loads(s) for s in z.read('integration20_results/common_predictions.jsonl').decode().splitlines()]
        manifest=json.loads(z.read('integration20_results/common_input_manifest.json'))
        diagnostics=json.loads(z.read('integration20_results/common_automatic_diagnostics.json'))
    inputs,refs,package=load_common(root=root)
    if manifest!=inputs or len(rows)!=22 or meta['common_completed']!=22 or meta['checks_completed']!=16:
        raise ValueError('Incomplete integration20')
    if meta['profile']!=PROFILE or meta['status']!='completed_semantic_review_pending':raise ValueError('Unexpected source profile')
    for name,sha in meta['source_hashes'].items():
        raw=subprocess.check_output(['git','show',meta['source_commit']+':'+name],cwd=root).replace(b'\r\n',b'\n')
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Execution source differs')
    if [{'id':r['id'],'automatic':automatic(ref,r['record'])} for r,ref in zip(rows,refs)]!=diagnostics:
        raise ValueError('Saved automatic diagnostics differ')
    previous=audit14(root)
    raw=read_archive(root/'final/evidence/comparison_02/original_results.zip',COMPARISON_SHA)
    old={r['id']:r for r in [json.loads(s) for s in raw['integrated_fp16/predictions.jsonl'].decode().splitlines()]}
    notes={r['id']:r['judgement'] for r in previous['product_rows'] if r['profile']=='integrated_fp16'}
    domain_path=root/'final/evidence/domain_review46/scorecard_complete.json'
    verify_domain_bytes(domain_path.read_bytes())
    humans={r['id']:r for r in json.loads(domain_path.read_text(encoding='utf-8'))['domain_details']['integrated_fp16']}
    jobs=make_jobs(rows,old,notes,refs,humans)
    changed=[j['id'] for j in jobs if j['judgement'] is None]
    if changed!=['vis_01','vis_02','vis_03','vis_04','vis_05','vis_07_injection','vis_09_contrast','vis_10_rotation']:
        raise ValueError('Expected changed agenda differs; investigate, do not select notes')
    return {'version':'evaluation21-plan','profile':PROFILE,'source_archive_sha256':SHA20,
        'source_commit':meta['source_commit'],'common_inputs_sha256':package['inputs_canonical_sha256'],
        'rubric_sha256':rubric_fingerprint(),'jobs':jobs,'new_judge_ids':changed,
        'judge_transfers':14,'human_text_transfers':12,'human_images_pending':10,
        'raw_scores_adjusted':False,'systems_regenerated':False,'gold_in_judge_payload':False,
        'judge_mean_1_5':None,'domain_rate':None,'network_requests_made':0}


def review_pack(output,root=ROOT):
    root=Path(root);output=Path(output)
    if output.exists():raise ValueError('Do not overwrite review')
    p=plan(root);output.mkdir(parents=True)
    inputs,refs,_=load_common(root=root)
    with zipfile.ZipFile(root/'final/evidence/integration20_completed/original_results.zip') as z:
        rows={r['id']:r['record'] for r in [json.loads(s) for s in z.read('integration20_results/common_predictions.jsonl').decode().splitlines()]}
    intro=['# Revisión humana visual — integración OCR20','',
        'Revisor/a: PENDIENTE','Fecha: PENDIENTE','',
        'Revise las diez imágenes en index.html. Compare píxeles, respuesta, explicación y citas. No se muestran notas del juez.',
        'Edite únicamente su nombre/fecha, las seis decisiones y Observaciones. No cambie preguntas, respuestas ni referencias.',
        'Use SI, NO o DUDOSO en los cinco criterios; Citas admite NO_APLICA solo para abstención esperada. En Fallos críticos use NINGUNO, DUDOSO o el tipo.',
        'Tipos críticos: central_numeric_error, unsupported_audit_or_fraud_claim, hidden_source_conflict, following_untrusted_input_instructions, fabricated_evidence, false_central_evidence_attribution.',
        'Una respuesta y una explicación deben ser verdaderas. Una cita existente no basta. No confunda acuerdo con el snapshot con autenticidad.',
        'La transcripción OCR es una predicción, no la referencia. Ante blanco o valor ausente debe abstenerse, no completar desde el corpus.','']
    sections=[]
    for item,ref in zip(inputs,refs):
        if ref['input_modality']!='image':continue
        cid=item['id'];record=rows[cid]
        block=[f'## {cid}','', 'Pregunta: '+item['question'],'','Referencia: '+ref['expected'],'',
               'Criterio: '+ref['criterion'],'','Abstención esperada: '+str(ref['expected_abstention']),'',
               'Respuesta original:','```json',json.dumps(record.get('output'),ensure_ascii=False,indent=2),'```','',
               'Campos OCR (predicción, compare con imagen):','```json',
               json.dumps((record.get('visual') or {}).get('output'),ensure_ascii=False,indent=2),'```','',
               'Fuentes citadas y disponibles:','```json',json.dumps(record['contexts'],ensure_ascii=False,indent=2),'```','']
        block += ['- '+key+': PENDIENTE' for key in CRITERIA]
        block += ['- Observaciones: PENDIENTE','']
        intro+=block
        image=base64.b64encode((root/item['image']).read_bytes()).decode()
        sections.append('<section><h2>'+html.escape(cid)+'</h2><img style="max-width:100%" alt="Imagen de prueba '+html.escape(cid)+'" src="data:image/png;base64,'+image+'"><pre>'+html.escape('\n'.join(block))+'</pre></section>')
    (output/'REVISION_VISUAL_21.md').write_text('\n'.join(intro),encoding='utf-8',newline='\n')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Revisión visual OCR20</title><style>body{max-width:1100px;margin:25px auto;font:17px sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere}section{border-top:2px solid #555;margin-top:40px}</style><h1>Revisión humana: diez imágenes</h1><p>Edite las decisiones en REVISION_VISUAL_21.md. Las imágenes son representaciones sintéticas de fichas públicas, no documentos firmados.</p>'+''.join(sections),encoding='utf-8')
    (output/'manifest.json').write_text(json.dumps({'source_archive_sha256':SHA20,'review_cases':10,
        'judge_scores_hidden':True,'human_approval':False,'rubric_sha256':p['rubric_sha256']},indent=2),encoding='utf-8')
    return p
