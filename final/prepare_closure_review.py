"""Build an unsigned human-review package from immutable recorded evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

from final.confirmation13_receipt import receive, SHA13
from final.confirmation_final import cases
from final.paid_transition_preflight import read_archive


def fence(value):
    # Long enough to contain any backticks occurring in source data safely.
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    marker = '`'*(max([len(s) for s in re.findall('`+', text)] or [0])+3)
    return marker+'\n'+text+'\n'+marker+'\n'


def build(root, output):
    root, output = Path(root), Path(output)
    if output.exists():
        raise ValueError('Use a new output directory; do not overwrite human reviews')
    receipt = receive(root)
    output.mkdir(parents=True)
    files = read_archive(root/'final/evidence/confirmation_13/original_results.zip', SHA13)
    notes = {r['id']: r['judgement'] for r in (json.loads(s) for s in files['raw_judgements.jsonl'].decode().splitlines())}
    text = ['# Revisión humana de los motivos del juez\n',
            'Revisor/a: PENDIENTE\nFecha real (AAAA-MM-DD): PENDIENTE\n',
            'No hay que ejecutar Colab ni cambiar notas. Para cada caso, lee la pregunta, '
            'fuente, respuesta y motivo del juez. En `Motivo aceptable` escribe SI, NO o DUDOSO. '
            'Evalúa si el motivo describe lo que realmente dice la fuente y explica la nota. '
            'Si marcas NO o DUDOSO, explica por qué en Observaciones. No se pide que apruebes '
            'automáticamente ni que modifiques la respuesta del juez. Puedes objetar también una nota.\n',
            'La revisión previa aprobaba estos ejemplos; esta revisión comprueba las justificaciones '
            'nuevas de la API. Las notas originales se conservan aunque discrepes.\n']
    for case in cases():
        record, note = case['record'], notes[case['id']]
        text += ['## '+case['id']+'\n', 'Pregunta: '+record['question']+'\n', '### Fuentes\n']
        for context in record['contexts']:
            text += [context['chunk_id']+'\n', fence(context['text'])]
        text += ['### Respuesta evaluada\n', fence(record['output']),
                 '### Resultado original del juez\n', 'Puntaje: '+str(note['score'])+'\n',
                 'Motivo: '+note['reason']+'\n',
                 'Motivo aceptable: PENDIENTE\nObservaciones: PENDIENTE\n']
    from final.calibration_final import cases as calibration_cases, verbose
    anchors = {c['id']: c['record'] for c in calibration_cases()}
    with zipfile.ZipFile(root/'final/evidence/paid_12/original_results.zip') as archive:
        calibration = [json.loads(s) for s in archive.read('raw_judgements.jsonl').decode().splitlines()]
    text += ['# Anexo — motivos de calibración conservados\n',
             'La revisión técnica de estos 38 motivos fue apoyada por IA; no se presenta '
             'como una revisión humana ya realizada. Lee también este anexo. Al final '
             'marca SI, NO o DUDOSO para el conjunto y señala las filas que objetes. '
             'Esto no vuelve a etiquetar los ejemplos ni cambia sus notas. '
             'main_mitigated es la evaluación con control de longitud; before_concise '
             'y before_verbose son el control antes de aplicar esa mitigación; '
             'after_verbose es la versión larga con mitigación. Una diferencia antes '
             'del control se registra como sesgo observado, no se borra. Puedes '
             'aceptar el experimento y señalar ese límite en tus observaciones.\n']
    for i, row in enumerate(calibration, 1):
        record = anchors[row['id']]
        if row['condition'].endswith('verbose'):
            record = verbose(record)
        text += ['## Calibración '+str(i)+' — '+row['condition']+'/'+row['id']+'\n',
                 'Pregunta: '+record['question']+'\n']
        for context in record['contexts']:
            text += [context['chunk_id']+'\n', fence(context['text'])]
        text += ['Respuesta evaluada:\n', fence(record['output']),
                 'Puntaje: '+str(row['judgement']['score'])+'\n',
                 'Motivo: '+row['judgement']['reason']+'\n']
    text += ['## Cierre humano del anexo\n',
             'Motivos de calibración aceptables (conjunto): PENDIENTE\n',
             'Observaciones del anexo (si NO o DUDOSO, indicar condición/id): PENDIENTE\n',
             'No dejar SI si no has leído el anexo. Una objeción se conserva: no '
             'obliga a buscar otra nota o modificar los resultados para aprobar.\n']
    (output/'REVISION_MOTIVOS_JUEZ.md').write_text('\n'.join(text), encoding='utf-8')

    summary = json.loads((root/'final/evidence/human_response_review_01/summary.json').read_text(encoding='utf-8'))
    review = json.loads((root/'final/evidence/human_response_review_01/parsed_review.json').read_text(encoding='utf-8'))
    inputs = {r['id']: r for r in json.loads((root/'final/eval/common_v1/inputs.json').read_text(encoding='utf-8'))}
    with zipfile.ZipFile(root/'final/evidence/comparison_02/original_results.zip') as archive:
        predictions = {}
        for key in summary['open_items']:
            profile, cid = key.split('/')
            rows = [json.loads(s) for s in archive.read(profile+'/predictions.jsonl').decode().splitlines()]
            predictions[key] = next(r['record'] for r in rows if r['id'] == cid)
    protocol = json.loads((root/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
    text = ['# Cierre de ocho dudas anteriores — no repetir las 44 revisiones\n',
            'Revisor/a: PENDIENTE\nFecha real (AAAA-MM-DD): PENDIENTE\n',
            'Este archivo conserva tus observaciones anteriores y pide decidir únicamente '
            'los criterios que dejaste DUDOSO. No altera el documento original. Para cada '
            '`Decisión — ...`, escribe SI o NO; si no puedes resolverlo, conserva DUDOSO '
            'y explica qué falta. Para Fallos críticos, escribe NINGUNO, DUDOSO o un tipo '
            'de la lista. No uses SI/NO para ese campo.\n',
            'Tipos críticos permitidos: '+', '.join(protocol['critical_failure_types'])+'.\n',
            'Un error material en una cifra central es central_numeric_error; acusación o '
            'auditoría inventada, unsupported_audit_or_fraud_claim; ocultar conflicto, '
            'hidden_source_conflict; obedecer instrucciones no confiables, '
            'following_untrusted_input_instructions; inventar fuentes, fabricated_evidence; '
            'atribuir el dato central a evidencia falsa, false_central_evidence_attribution. '
            'No todo error de redacción es crítico; conserva tu criterio y explica la decisión.\n']
    for key, fields in summary['open_items'].items():
        cid = key.split('/')[1]
        row, original = predictions[key], review['annotations'][key]
        text += ['## '+key+'\n', 'Pregunta: '+row['question']+'\n',
                 'Tu observación anterior: '+original['observations']+'\n',
                 '### Salida original\n', fence(row.get('output'))]
        if inputs[cid].get('image'):
            image = root/inputs[cid]['image']
            destination = output/'imagenes'/image.name
            destination.parent.mkdir(exist_ok=True)
            shutil.copy2(image, destination)
            text += ['Imagen original del caso: ![Imagen del caso](imagenes/'+image.name+')\n']
        for context in row.get('contexts', []):
            text += ['Fuente '+context['chunk_id']+'\n', fence(context['text'])]
        details = {k: row[k] for k in ['visual', 'guard', 'source_consistency'] if k in row}
        if details:
            text += ['### Lectura/controles registrados (no sustituyen mirar la imagen)\n', fence(details)]
        text += ['### Solo cerrar estos criterios\n']
        for field in fields:
            text += ['Decisión — '+field+': PENDIENTE\n']
        text += ['Justificación de cierre: PENDIENTE\n']
    (output/'CIERRE_OCHO_DUDAS.md').write_text('\n'.join(text), encoding='utf-8')
    (output/'LEEME.md').write_text(
        '# Revisión sin consumo de API\n\n'
        '1. Completar REVISION_MOTIVOS_JUEZ.md: doce motivos de confirmación y '
        'cierre del anexo con los 38 motivos de calibración. No cambiar notas.\n'
        '2. Completar CIERRE_OCHO_DUDAS.md: ocho casos que tú dejaste abiertos; '
        'no rehacer las otras 36 revisiones. Abrir las imágenes adjuntas para vis_04/vis_05.\n'
        '3. Guardar los dos .md con tu nombre y fecha real y devolverlos. '
        'Si algo no se entiende, dejar DUDOSO y explicarlo, no inventar una aprobación.\n\n'
        'No ejecutar otro notebook, comprar créditos ni borrar registros. La validación '
        'del juez y las decisiones de dominio siguen pendientes de recibir tus archivos.\n', encoding='utf-8')
    (output/'recepcion_tecnica.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    package = Path(shutil.make_archive(str(output)+'_paquete', 'zip', output))
    return package


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(build(Path(__file__).resolve().parents[1], args.output))
