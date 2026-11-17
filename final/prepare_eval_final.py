"""Assemble existing approved inputs/references and synthetic judge-review anchors. No inference."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from final.calibration_final import cases,ACCEPTANCE


def canonical_hash(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def build_common(folder):
    if folder.exists():raise FileExistsError('Do not overwrite eval package')
    gold=json.loads((ROOT/'m3/eval/gold_v1/eval_set.json').read_text(encoding='utf-8'))
    visual=ROOT/'final/eval/visual_candidates_v1'
    if gold.get('status')!='human_reviewed' or any(c.get('review_status') not in {'approved','approved_correction_applied'} for c in gold['cases']):
        raise ValueError('QA source lacks recorded human approval')
    from final.visual_probe import load_inputs
    load_inputs(visual)
    approval=json.loads((visual/'human_approval.json').read_text(encoding='utf-8'))
    if hashlib.sha256((visual/'references_for_human_review.json').read_bytes()).hexdigest()!=approval['references_sha256']:
        raise ValueError('Visual references differ from human approval')
    manifest=json.loads((visual/'manifest.json').read_text(encoding='utf-8'))
    visual_refs=json.loads((visual/'references_for_human_review.json').read_text(encoding='utf-8'))
    inputs=[];references=[]
    for c in gold['cases']:
        inputs.append({'id':c['eval_id'],'question':c['input'],'image':None,'image_sha256':None})
        facts=c['required_facts']
        if c['kind']=='inconsistency':
            facts=re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?',c['expected'])
        references.append({'id':c['eval_id'],'kind':c['kind'],'input_modality':'text',
            'expected':c['expected'],'criterion':c['criterion'],'required_facts':facts,
            'source_ids':c['source_ids'],'expected_abstention':c['kind']=='unanswerable',
            'pair_with':None,'provenance':'m3-qa-gold-1.0, human review 2026-10-28, already inspected historically'})
    by_id={r['id']:r for r in visual_refs}
    for c in manifest:
        r=by_id[c['id']]
        inputs.append({'id':c['id'],'question':c['question'],
                       'image':'final/eval/visual_candidates_v1/'+c['image'],'image_sha256':c['sha256']})
        facts=[] if r['expected_abstention'] else [r['expected_visual_fields']['modalidad'],r['expected_visual_fields']['valor_cop']]
        references.append({'id':c['id'],'kind':c['kind'],'input_modality':'image',
            'expected':('Abstención justificada.' if r['expected_abstention'] else 'Modalidad: '+facts[0]+'. Valor (COP): '+facts[1]+'.'),
            'criterion':r['criterion'],'required_facts':facts,'source_ids':[r['source_id']] if r['source_id'] else [],
            'expected_visual_fields':r['expected_visual_fields'],'expected_abstention':r['expected_abstention'],
            'pair_with':c['pair_with'],'provenance':'visual v1, user human approval 2026-11-16; already used in development visual03'})
    folder.mkdir(parents=True)
    write_json(folder/'inputs.json',inputs)
    write_json(folder/'references.json',references)
    write_json(folder/'metadata.json',{'version':'common-eval-candidate-1','status':'assembled_not_frozen',
        'cases':len(inputs),'text_cases':12,'image_cases':10,'independent_contract_count_not_22':True,
        'inputs_canonical_sha256':canonical_hash(inputs),'references_canonical_sha256':canonical_hash(references),
        'qa_source_canonical_sha256':canonical_hash(gold),'visual_refs_source_canonical_sha256':canonical_hash(visual_refs),
        'new_human_labels_created':False,'model_inference_performed':False,
        'caveat':'Derived from approved references, not new blind gold. Common harness/control definitions still to freeze; no change to historical artifacts.'})
    return inputs,references


def build_calibration_review(folder):
    if folder.exists():raise FileExistsError('Do not overwrite calibration review')
    folder.mkdir(parents=True)
    anchors=cases()
    write_json(folder/'anchors.json',anchors)
    write_json(folder/'rules.json',ACCEPTANCE)
    lines=['# Revisión de anclas sintéticas del juez', '',
           'Estado: PENDIENTE. No son resultados del modelo: son respuestas propuestas para comprobar si el juez distingue contenido respaldado de errores.', '',
           'Abra index.html. En cada caso compare pregunta, fuentes, respuesta y explicación. Compruebe si el rango de nota propuesto tiene sentido según la evidencia. No necesita dar una nota exacta.', '',
           'APROBADO significa que acepta usar ese ejemplo y ese rango en la calibración; no que toda respuesta del ejemplo sea buena. Los casos bad deben ser malos deliberadamente. Si discrepa, marque CORREGIR e indique por qué.', '',
           'Compruebe especialmente number_bad (cero añadido), conflict_good (abstención ante dos cifras), attribution_bad (respuesta corta correcta pero explicación falsa) y empty_explanation_bad (explicación vacía).', '',
           'Revisor/a: PENDIENTE','Fecha: PENDIENTE','']
    lines += ['- '+c['id']+': PENDIENTE. Observaciones: ' for c in anchors]
    (folder/'REVISION_CALIBRACION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    sections=[]
    for c in anchors:
        sections.append('<section><h2>'+html.escape(c['id'])+'</h2><p>Rango propuesto: '+str(c['expected_score_range'][0])+'–'+str(c['expected_score_range'][1])+'</p><pre>'+html.escape(json.dumps(c['record'],ensure_ascii=False,indent=2))+'</pre></section>')
    (folder/'index.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>Revisión de calibración ContractRisk</title><style>body{font:18px system-ui;max-width:1000px;margin:30px auto;padding:15px}pre{white-space:pre-wrap;background:#f3f5f7;padding:18px}section{border-top:2px solid #456;margin-top:30px}</style><h1>Anclas propuestas — revisión humana pendiente</h1><p>20 ejemplos ficticios, no contratos reales ni respuestas generadas por el juez. Revise los rangos y complete REVISION_CALIBRACION.md.</p>'+''.join(sections)+'</html>',encoding='utf-8',newline='\n')
    write_json(folder/'metadata.json',{'status':'human_review_pending','anchors':20,'anchor_canonical_sha256':canonical_hash(anchors),
        'rules_canonical_sha256':canonical_hash(ACCEPTANCE),'model_inference_performed':False,
        'authorship':'AI-assisted synthetic anchors, human approval not yet received'})


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--common',type=Path,required=True)
    p.add_argument('--calibration',type=Path,required=True)
    p.add_argument('--zip',type=Path,required=True)
    args=p.parse_args()
    if any(p.exists() for p in [args.common,args.calibration,args.zip]):raise FileExistsError('Use new output paths')
    build_common(args.common);build_calibration_review(args.calibration)
    args.zip.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.zip,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(args.calibration.rglob('*')):
            if file.is_file():z.write(file,file.relative_to(args.calibration))
    print('22 common cases assembled (not frozen); 20 synthetic calibration anchors pending human review. No inference.')
