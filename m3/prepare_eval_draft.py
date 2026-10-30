"""Generate a traceable QA DRAFT for human review, never an approved gold set."""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    capture = json.loads((ROOT / 'corpus/source_snapshot.json').read_text(encoding='utf-8'))
    rows = capture['records']
    docs = {d['doc_id']: d for d in map(json.loads, (ROOT / 'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines())}
    cases = []

    def add(question, expected, criterion, sources, kind='factual', facts=None):
        cases.append({'eval_id': f'm3_{len(cases)+1:03d}', 'input': question,
                      'expected': expected, 'criterion': criterion, 'source_ids': sources,
                      'kind': kind, 'required_facts': facts or [], 'review_status': 'pending',
                      'reviewer': '', 'review_notes': ''})

    # One contract from every stratum; remaining records stay as retrieval distractors.
    for index in [0, 4, 8, 12, 16, 20]:
        r = rows[index]
        cid = r['id_contrato']
        add(f'Según la ficha {cid}, ¿qué se contrata y qué entidad lo contrata?',
            f"Entidad: {r['nombre_entidad']}. Descripción registrada: {r['descripcion_del_proceso']}",
            'Identificar entidad y actividad/objeto sin añadir obligaciones ausentes; justificar con la ficha citada.',
            [cid], facts=[r['nombre_entidad'], r['descripcion_del_proceso']])
    for a, b in [(0, 1), (4, 5)]:
        x, y = rows[a], rows[b]
        vx, vy = Decimal(x['valor_del_contrato']), Decimal(y['valor_del_contrato'])
        diff = abs(vx-vy)
        add(f"¿Cuál es la diferencia absoluta entre los valores registrados de {x['id_contrato']} y {y['id_contrato']}? Explica la operación y cita ambas fichas.",
            f"|{vx} - {vy}| = {diff}, usando los valores registrados en ambas fichas.",
            'Recuperar ambos valores, calcular la diferencia absoluta exacta, mostrar la operación y citar ambas fuentes. No inferir sobrecosto.',
            [x['id_contrato'], y['id_contrato']], 'calculation', [str(vx), str(vy), str(diff)])
    r = rows[0]
    cid = r['id_contrato']
    add(f'¿Las fechas de firma e inicio registradas en {cid} son cronológicamente consistentes? ¿Podemos concluir por eso que hubo una irregularidad?',
        f"La ficha registra firma {r['fecha_de_firma']} e inicio {r['fecha_de_inicio_del_contrato']}. El inicio figura antes de la firma registrada. La ficha sola no explica la discrepancia ni permite concluir una irregularidad.",
        'Citar ambas fechas, señalar su orden y la incertidumbre; no corregir fechas ni atribuir causas o acusaciones.',
        [cid], 'inconsistency')
    add(f'¿Qué modalidad de contratación registra la ficha {rows[1]["id_contrato"]}?',
        rows[1]['modalidad_de_contratacion'], 'Responder la modalidad registrada y citar la ficha, sin explicación jurídica inventada.',
        [rows[1]['id_contrato']], facts=[rows[1]['modalidad_de_contratacion']])
    add(f'¿Cuál es el texto literal de la cláusula de multas del contrato {cid}?',
        'No dispongo del texto de esa cláusula en estas fuentes. Se necesita consultar el documento contractual completo.',
        'Abstenerse de inventar cláusulas o porcentajes. Explicar que las fichas disponibles no incluyen el clausulado.',
        [], 'unanswerable')
    add(f'¿Qué concluyó la auditoría de ejecución física sobre el contrato {rows[4]["id_contrato"]}?',
        'Las fuentes disponibles no contienen un informe de auditoría de ejecución física. No puedo afirmar su conclusión.',
        'Abstenerse: no equiparar estado contractual o valor registrado con evidencia de ejecución física o auditoría.',
        [], 'unanswerable')
    payload = {'version': 'm3-qa-draft-0.1', 'status': 'pending_human_review',
               'authorship': 'AI-assisted draft grounded in frozen SECOP records; no human approval yet',
               'cases': cases}
    target = ROOT / 'eval'
    target.mkdir(exist_ok=True)
    (target / 'eval_set_draft.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    content = ['# Revisión humana del borrador QA M3',
               'Estado: pendiente. No es un gold aprobado. Son 12 preguntas, incluidas dos de cálculo y dos sin respuesta en el corpus.',
               '## Instrucciones',
               'En cada caso cambia PENDIENTE por APROBADO o CORREGIR. Si corriges, escribe tu propuesta y el motivo. Añade tu nombre y fecha. Revisa las fichas completas al final, no solo la respuesta propuesta. Puedes devolver este Markdown editado o enviar las decisiones por número en el chat. No hace falta ejecutar Python.',
               'Para las preguntas sin respuesta, revisa todo el corpus: no basta con que un buscador no encuentre el dato. Las fichas son registros, no contratos completos. Los enlaces online pueden cambiar; la referencia de este ejercicio es la captura congelada adjunta aquí.',
               'Revisor: PENDIENTE\n\nFecha: PENDIENTE']
    for c in cases:
        content += [f"## {c['eval_id']} — {c['kind']}", f"**Pregunta:** {c['input']}",
                    f"**Respuesta propuesta:** {c['expected']}", f"**Criterio:** {c['criterion']}",
                    '**Fuentes:** ' + (', '.join(c['source_ids']) or 'Comprobar ausencia en las 24 fichas del anexo'),
                    '**Decisión:** PENDIENTE\n\n**Corrección/comentario:**']
    content += ['# Anexo: las 24 fichas del corpus congelado',
                'Estas fuentes no incluyen etiquetas ni respuestas de evaluación. La ausencia de un dato no prueba un hecho negativo sobre el contrato.']
    for d in docs.values():
        content += [f"## {d['doc_id']}", f"[Consultar origen público]({d['source_url']})", '```text\n'+d['text']+'\n```']
    (target / 'REVISION_HUMANA_QA.md').write_text('\n\n'.join(content)+'\n', encoding='utf-8', newline='\n')
    # Development questions are distinct from the final QA questions. They must
    # not later be relabelled as held-out evaluation after prompt tuning.
    dev = [{'input': f"¿Qué modalidad registra {rows[i]['id_contrato']}?",
            'expected': rows[i]['modalidad_de_contratacion'], 'source_ids': [rows[i]['id_contrato']]}
           for i in [3, 7, 11, 15]]
    (target / 'development_questions.json').write_text(json.dumps({'purpose': 'development_only_not_final_scorecard', 'cases': dev}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Created {len(cases)} draft evaluation questions and {len(dev)} development questions. Human review pending.')


if __name__ == '__main__':
    build()
