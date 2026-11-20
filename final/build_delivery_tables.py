"""Reproduce delivery tables from preserved evidence without models or paid keys."""
import argparse
import json
from pathlib import Path
import zipfile

from final.evaluation21 import ROOT
from final.domain_closure15 import build as historic_scorecard
from final.evaluation21_audit import audit as ocr_scorecard
from final.audit_space23_logs import audit as service_logs
from final.score_visual_probe import percentile

LABELS={'qa_no_rag_fp16':'Control QA sin RAG','m3_text_fp16':'M3 textual',
        'integrated_fp16':'Integrado visual FP16','integrated_nf4':'Integrado visual NF4',
        'integrated_no_tool_fp16':'FP16 sin herramienta'}


def build(root=ROOT):
    root=Path(root)
    historic=historic_scorecard(root)
    saved=json.loads((root/'final/evidence/domain_review46/scorecard_complete.json').read_text(encoding='utf-8'))
    if historic!=saved:raise ValueError('Historical domain scorecard does not reproduce')
    ocr=ocr_scorecard(root)
    if ocr!=json.loads((root/'final/evidence/evaluation21_completed/scorecard.json').read_text(encoding='utf-8')):
        raise ValueError('OCR scorecard does not reproduce')
    logs=service_logs(root/'final/evidence/space_ocr23_cpu/container_smoke_original.txt')
    rows=[]
    for row in historic['tables']:
        rows.append({'profile':row['profile'],'label':LABELS[row['profile']],
            'cases':22,'literal_coverage':row['literal_coverage_mean'],'judge_mean':row['judge_mean'],
            'domain_pass':row['domain_pass_count'],'domain_rate':row['domain_rate'],
            'p50_seconds':row['p50_seconds'],'p95_seconds':row['p95_seconds'],
            'peak_cuda_gib':row['peak_cuda_allocated_bytes']/1024**3,
            'visual_cases_received':10,'visual_reader':row['profile'].startswith('integrated'),
            'timing_scope':'comparison02_common_T4_single_session'})
    with zipfile.ZipFile(root/'final/evidence/integration20_completed/original_results.zip') as z:
        predictions=[json.loads(s) for s in z.read('integration20_results/common_predictions.jsonl').decode().splitlines()]
    times=[r['wall_seconds'] for r in predictions]
    rows.append({'profile':ocr['profile'],'label':'Final OCR FP16 (referencia Colab)',
        'cases':22,'literal_coverage':ocr['literal_fact_coverage_mean'],'judge_mean':ocr['judge_mean_1_5'],
        'domain_pass':ocr['domain_pass_count'],'domain_rate':ocr['domain_rate'],
        'p50_seconds':percentile(times,.5),'p95_seconds':percentile(times,.95),
        'peak_cuda_gib':None,'visual_cases_received':10,'visual_reader':True,
        'timing_scope':'integration20_wall_seconds_other_T4_session_no_efficiency_claim'})
    return {'rows':rows,'common_cases':22,'text_cases':12,'image_cases':10,
        'efficiency_decision':historic['efficiency_decision'],
        'service_events':{'accepted':logs['accepted_smoke_events'],'rejected':logs['rejected_input_events'],
                          'total':logs['total_events'],'runtime_errors':logs['runtime_error_events']},
        'estimated_reserved_budget_usd':ocr['estimated_or_reserved_total_usd'],
        'paid_calls_made_by_reproduction':0,'new_inference_performed':False,
        'limitations':['Control QA sin RAG adapts the task, not the historical M2 classifier.',
                       'OCR latency is descriptive wall time from another T4 session; no speedup or memory claim.',
                       'Public ZeroGPU measurements are not mixed with Colab efficiency measurements.',
                       'Public W&B run Crashed continuity issue remains unresolved.']}


def markdown(result):
    lines=['# Tablas reproducibles de la entrega','',
        '| Perfil | Cobertura literal | Juez /5 | Dominio /22 | p50 s | p95 s | Pico CUDA GiB |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        memory='No medido' if r['peak_cuda_gib'] is None else f"{r['peak_cuda_gib']:.3f}"
        lines.append(f"| {r['label']} | {r['literal_coverage']:.3f} | {r['judge_mean']:.3f} | {r['domain_pass']}/22 | {r['p50_seconds']:.3f} | {r['p95_seconds']:.3f} | {memory} |")
    lines += ['', 'Cobertura es un diagnóstico, no exactitud. Los cinco perfiles de comparación02',
              'comparten sesión TeslaT4. OCR20 usa otra sesión TeslaT4 y tiempo de pared del',
              'harness, sin control equivalente de calentamiento/sincronización: su latencia',
              'es descriptiva, no evidencia de aceleración. No se midió memoria OCR.',
              'Los perfiles textuales reciben diez imágenes pero se abstienen sin leerlas.',
              'El control sin RAG es adaptación QA, no el clasificador M2 original.','']
    return '\n'.join(lines)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Use a new directory; do not overwrite evidence')
    result=build();a.output.mkdir(parents=True)
    (a.output/'tables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (a.output/'tables.md').write_text(markdown(result),encoding='utf-8',newline='\n')
    print(json.dumps({'profiles':len(result['rows']),'domain_ocr':result['rows'][-1]['domain_pass'],
                      'paid_calls':0,'output':str(a.output)},ensure_ascii=False))
