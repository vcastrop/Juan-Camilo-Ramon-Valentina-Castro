# Piloto del juez y corrección de la rúbrica

## Corrida diagnóstica

La primera ejecución utilizó `Qwen/Qwen2.5-0.5B-Instruct` y la rúbrica `judge_rubric_v1.json`. El parser logró extraer el 100 % de las respuestas, pero el modelo no aplicó de forma consistente las anclas:

- Los cuatro errores de clasificación (`m2_003`, `m2_004`, `m2_008` y `m2_018`) recibieron puntaje 4, aunque las etiquetas predicha y esperada eran diferentes.
- Cuatro etiquetas correctas (`m2_014`, `m2_015`, `m2_016` y `m2_019`) recibieron puntaje 1.
- La prueba de verbosidad asignó 1 tanto a la respuesta concisa como a la extensa. La diferencia fue cero, pero esos niveles no eran compatibles con una etiqueta correcta.

Por tanto, el promedio 3,4 y la tasa de aprobación 0,8 de esa corrida no se aceptan como evidencia final del juez. Que el parser funcione no demuestra que el veredicto sea válido.

## Causa observada

El modelo de 0,5B produjo respuestas JSON válidas, pero en varios casos repitió fragmentos de la instrucción o afirmó que etiquetas distintas coincidían. El problema fue seguimiento de la rúbrica, no extracción técnica del puntaje.

## Mitigación aplicada

La versión `judge_rubric_v1_1.json`:

1. cambia el juez a `Qwen/Qwen2.5-1.5B-Instruct`;
2. presenta al comienzo del prompt ambas etiquetas y el resultado de su comparación exacta;
3. restringe explícitamente los niveles permitidos según coincidan o no;
4. aplica una salvaguarda auditable y conserva `judge_raw_score`, `judge_score` y `judge_guardrail_applied` por fila;
5. mantiene el control de verbosidad y la tasa de parsing como resultados visibles.

Los archivos de la primera corrida se conservan en `evidence/judge_pilot_v1_0/` únicamente para trazabilidad y no constituyen el scorecard final.
