# Revisión de respuestas recibida, con dudas preservadas

El archivo declarado por Juan Camilo Ramon Perez, fecha 18/11/2026, contiene las 44 respuestas revisadas. Se conserva [el original sin editar](original_review.md), incluidos su estado PENDIENTE y comentarios. [Transcripción estructurada](parsed_review.json), [análisis derivado sin notas del juez](summary.json).

Hay ocho casos con al menos un DUDOSO: FP16 m3_004, NF4 m3_005, FP16 m3_006, FP16 m3_009, NF4 m3_009, vis_04 de ambos perfiles y FP16 vis_05. No se los cierra en nombre del revisor; tampoco se amplían retrospectivamente las categorías críticas para forzar un resultado. Las observaciones de revisión son humanas declaradas; el análisis estructurado y esta recepción son asistencia técnica de IA, no una segunda revisión humana.

## Decisión que sí está sustentada

NF4 m3_001 tiene el código crítico explícito `false_central_evidence_attribution`: afirma «Aeroclínico» en vez de AEROCIVIL. FP16 no tiene ese fallo en ese mismo caso. Es un fallo crítico nuevo por caso/tipo bajo las reglas previas. Además, los dos pares de invarianza tienen respuestas completas en FP16 y omisiones en NF4; repetir la misma respuesta incompleta no satisface el control semántico de «ambas correctas».

Por esos vetos confirmados **NF4 no se acepta para el despliegue**. No hace falta fingir una nota LLM para no publicar una configuración que incumple esas condiciones. Esto no aprueba FP16: también tiene omisiones, errores y dudas. La evaluación numérica completa de eficiencia permanece `not_evaluable` porque el juez y parte de la auditoría semántica siguen pendientes. No se modifica el algoritmo original de aceptación para ocultarlo.

## Fe de erratas de denominador

La observación general dice «6 de los 8 casos visuales no bloqueados». El conjunto tiene ocho preguntas visuales respondibles que piden modalidad/valor; una (`vis_04`) fue bloqueada. Por tanto, la omisión del monto ocurre en **6 de 7 no bloqueadas**, o 6 de 8 si se incluye también la bloqueada en el denominador. El original no se corrige silenciosamente.

La revisión humana no sustituye las notas del juez. Las referencias, respuestas, rúbrica y resultados originales permanecen intactos. Se continuará con diagnóstico acotado de la API y calificación posterior de las mismas respuestas, sin repetir los modelos para seleccionar mejores resultados.
