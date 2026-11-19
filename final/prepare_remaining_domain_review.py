"""Build only the 46 unresolved semantic reviews, no API calls or prefilling decisions."""
import argparse
import json
from pathlib import Path
import shutil

from final.domain_scorecard14 import build
from final.prepare_closure_review import fence
from final.paid_transition_preflight import read_archive
from final.prepare_product_judge_plan import COMPARISON_SHA


def prepare(root, folder):
    root, folder = Path(root), Path(folder)
    if folder.exists(): raise ValueError('Do not overwrite a human review folder')
    result = build(root)
    pending = result['pending_semantic_keys']
    if len(pending) != 46: raise ValueError('Pending population changed; inspect before preparing a new review')
    inputs = {r['id']: r for r in json.loads((root/'final/eval/common_v1/inputs.json').read_text(encoding='utf-8'))}
    refs = {r['id']: r for r in json.loads((root/'final/eval/common_v1/references.json').read_text(encoding='utf-8'))}
    protocol = json.loads((root/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
    files = read_archive(root/'final/evidence/comparison_02/original_results.zip', COMPARISON_SHA)
    originals = {p: {r['id']: r['record'] for r in (json.loads(s) for s in files[p+'/predictions.jsonl'].decode().splitlines())}
                 for p in {key.split('/')[0] for key in pending}}
    folder.mkdir(parents=True)
    text = ['# Revisión de dominio pendiente — 46 salidas, sin repetir las anteriores\n',
            'Revisor/a: PENDIENTE\nFecha real: PENDIENTE\n',
            'Se incluyen 22 salidas Sin RAG, 22 M3 textual y solo los dos cálculos '
            'distintos de la ablación sin herramienta. Las otras veinte salidas '
            'de esa ablación tienen mismo caso, respuesta y evidencia que FP16 '
            'y reutilizan su anotación por equivalencia explícita; no se afirma '
            'que las hayas revisado de nuevo. Las 44 revisiones anteriores no se repiten.\n',
            'Para cada campo usa SI, NO o DUDOSO. En Citas se permite NO_APLICA '
            'solo para una abstención esperada que no necesite citas. En Fallos '
            'críticos usa NINGUNO, DUDOSO o un tipo de la lista inferior. '
            'Completa Observaciones con una razón concreta y tu nombre/fecha reales.\n',
            'Tipos críticos: '+', '.join(protocol['critical_failure_types'])+'.\n',
            'Una abstención honesta no demuestra por sí sola resolver la tarea. '
            'Considera el criterio de referencia y si faltaba la información en '
            'la entrada o si el sistema simplemente no soporta esa modalidad. '
            'La completitud semántica considera respuesta y explicación, como '
            'en tu cierre anterior. No inventes obligaciones, pruebas de fraude '
            'o auditorías. No cambies respuestas ni referencias para aprobarlas.\n',
            'Las notas del juez se omiten aquí para no condicionar tu revisión. '
            'No hay que ejecutar Colab ni pagar llamadas.\n']
    manifest = []
    fields = ['Respuesta respaldada', 'Explicación respaldada y no vacía', 'Completa para lo preguntado',
              'Citas respaldan lo afirmado', 'Abstención adecuada', 'Fallos críticos']
    for key in pending:
        profile, cid = key.split('/')
        record = originals[profile][cid]
        manifest.append({'review_key': key, 'profile': profile, 'id': cid})
        text += ['## '+key+'\n', 'Pregunta: '+record['question']+'\n',
                 'Referencia: '+refs[cid]['expected']+'\n', 'Criterio: '+refs[cid]['criterion']+'\n',
                 'Abstención esperada: '+str(refs[cid]['expected_abstention'])+'\n',
                 '### Salida estructurada original\n', fence(record.get('output'))]
        if record.get('output') is None:
            text += ['No hubo salida estructurada utilizable. Los intentos originales '
                     'se muestran como diagnóstico; no los sustituyas por una respuesta nueva.\n',
                     fence(record.get('answer_attempts', []))]
        if inputs[cid].get('image'):
            image = root/inputs[cid]['image']
            destination = folder/'imagenes'/image.name
            destination.parent.mkdir(exist_ok=True)
            shutil.copy2(image, destination)
            text += ['Entrada de la tarea: ![Imagen](imagenes/'+image.name+')\n',
                     'El perfil textual no dispone de lector visual; no recibió una transcripción gold.\n']
        for context in record.get('contexts', []):
            text += ['Fuente '+context['chunk_id']+'\n', fence(context['text'])]
        text += ['### Revisión humana\n']+[field+': PENDIENTE\n' for field in fields]+['Observaciones: PENDIENTE\n']
    (folder/'REVISION_DOMINIO_PENDIENTE.md').write_text('\n'.join(text), encoding='utf-8')
    (folder/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (folder/'LEEME.md').write_text(
        '# Cierre de dominio sin consumo de API\n\n'
        'Completa REVISION_DOMINIO_PENDIENTE.md con nombre y fecha reales y devuelve '
        'ese archivo. Puedes hacerlo tú o un integrante que efectivamente lo revise. '
        'Son 46 salidas pendientes, no 110 nuevas revisiones. Incluye las imágenes '
        'de referencia. No cambies las respuestas y conserva DUDOSO si falta algo.\n\n'
        'Las instrucciones están al inicio del archivo. No hay que ejecutar '
        'notebooks, comprar créditos ni repetir evaluaciones.\n', encoding='utf-8')
    return Path(shutil.make_archive(str(folder)+'_paquete', 'zip', folder))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(prepare(Path(__file__).resolve().parents[1], args.output))
