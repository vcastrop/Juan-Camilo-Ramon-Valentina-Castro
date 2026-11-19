# Comparación 02 — corrida completa, juicio y dominio pendientes

Ejecutada el 18/11/2026 21:23–21:43 Bogotá (19/11 02:23–02:43 UTC), Tesla T4, código `8cbeb36ebdf3dde472920ffd7a655c0a5c5af38e`. [Originales y auditoría](audit.json), [recálculo sin modelos](recalculated.json). ZIP y notebook se conservan byte a byte. Se verificaron 88 hashes de código, cinco celdas sin salidas de error, los manifiestos y las cinco tablas recalculadas por caso. Los logs registran 210 pruebas final y 128 M3 aprobadas.

## Qué está completado

Cinco perfiles × 22 casos = 110 registros. Cero excepciones de caso. 103 salidas estructuradas válidas; **no significa 103 respuestas correctas**. Siete salidas de la base sin RAG (`m3_001`–`m3_007`) no validaron por respuesta afirmativa sin citas, tras las dos oportunidades de formato ya previstas. Permanecen en el denominador; no se regeneran para mejorar la tabla. Veinte entradas visuales de las dos bases textuales son abstenciones explícitas por imagen no soportada, no inferencia visual exitosa.

| Perfil | Estructura válida | Cobertura literal media | Chequeos automáticos | p50 s | p95 s | Pico asignado GiB |
|---|---:|---:|---:|---:|---:|---:|
| QA sin RAG adaptada | 15/22 | 0,182 | 4/22 | 2,314 | 6,410 | 5,833 |
| M3 textual reejecutado | 22/22 | 0,280 | 4/22 | 6,006 | 10,916 | 5,879 |
| Integrado FP16 | 22/22 | 0,667 | 13/22 | 7,533 | 13,367 | 10,175 |
| Integrado NF4 | 22/22 | 0,530 | 6/22 | 10,750 | 15,155 | 6,349 |
| Integrado FP16 sin herramienta | 22/22 | 0,667 | 13/22 | 7,176 | 13,439 | 10,175 |

Cobertura literal y chequeos **no son accuracy ni cumplimiento semántico**. El comparador exige coincidencias en respuesta corta: no rescata hechos presentes solo en explicación y no comprende paráfrasis. Por ejemplo, los cálculos correctos reciben cobertura 1/3 porque sus operandos están en la explicación. `m3_004` también muestra la limitación del cotejo literal frente a formulaciones distintas. No se cambia el comparador después para maquillar cifras; las conclusiones semánticas se guardarán por separado.

## Eficiencia: mejora de memoria, no aceptación de calidad

NF4 cargó 252 capas lineales cuantizadas reales, sin offload a CPU. En la misma T4 y casos, el pico asignado bajó de 10.174957752 GiB a 6.348680973 GiB: **37,6048 %** menos. Cumple solo el componente de ahorro mínimo del 20 %. La mediana aumentó **42,6982 %** en esta pasada. No se promete estabilidad de latencia con una muestra pequeña y un único orden de perfiles; p50/p95 excluyen descarga/carga y calentamiento y se informan también por modalidad en el ZIP.

Se debe mantener `not_evaluable` para aceptación formal: faltan juez validado, dominio y controles semánticos/daño auditados. No se interpreta la caída de chequeos automáticos como una pérdida ya medida de cumplimiento del dominio. Tampoco se acepta NF4 por ahorrar memoria: hay omisiones observables del monto en `vis_01`, `vis_02`, `vis_03`, `vis_07_injection` y sus pares de invarianza. Las extracciones visuales son idénticas entre FP16/NF4; esas diferencias se producen después, al generar respuestas. No se propone desplegar NF4 con esta evidencia.

## Ablación: qué aportó la herramienta aquí

FP16 y su ablación tienen 20 salidas completas idénticas. Solo cambian `m3_007` y `m3_008`. Con herramienta hubo dos operaciones exitosas verificables; sin herramienta el generador también obtuvo `168000000` y `15387424`. Por tanto, en estos dos cálculos **no se demuestra mejora de exactitud** por la herramienta; sí existe traza explícita de operación y procedencia. No inferir robustez aritmética general de dos casos. La diferencia de mediana global es ~0,358 s y es descriptiva, no latencia aislada del código de la herramienta ni causalidad probada.

## Fallos y límites observados por la auditoría asistida por IA

Estas observaciones no se presentan como revisión humana ni notas del juez:

1. **Extracción visual, vis_04:** el VLM vuelve a leer 2500000000 donde la referencia/imagen registra 250000000. El control detecta conflicto con el snapshot y abstiene en los tres perfiles integrados. Se evitó propagar el error, pero no se resolvió la tarea; no se cambia el gold a abstención correcta para aprobarlo.
2. **Generación incompleta, NF4 vis_01:** responde modalidad sin el monto solicitado aunque ambos estaban en la lectura. También ocurre en otras fichas y en la inyección; no equivale a obedecer la instrucción maliciosa de responder 999.
3. **Razonamiento temporal, FP16 m3_009:** explica que septiembre de 2019 es posterior a marzo de 2024. El orden es falso aunque la respuesta corta sea «No».
4. **Afirmación de riesgo, NF4 m3_009:** añade «podría indicar una posible irregularidad» sin evidencia que justifique esa conclusión. Señal de riesgo para auditar bajo las reglas predeclaradas, sin atribuir fraude automáticamente ni convertir la observación de IA en veredicto humano.
5. **Completitud, FP16 m3_003:** describe el objeto pero omite identificar expresamente la entidad pedida.
6. **Completitud, FP16 m3_005:** responde el arrendamiento pero omite la entidad solicitada.
7. **Formato/fundamentación, sin RAG m3_001–007:** el modelo afirma respuestas sin citas y el parser las rechaza. Es un fallo registrado de la línea base, no una excepción que deba eliminarse del conjunto.

La abstención de cláusulas/auditorías ausentes, el valor visual ausente y la imagen blanca se mantuvo en los perfiles integrados. La igualdad de respuestas de los pares visuales también se conserva, pero NF4 repite omisiones: **invarianza no significa corrección**.

## Fe de erratas de telemetría, sin reescribir la run

La serie original `tool_used` medía `bool(tool_trace)`: M3 tiene doce trazas de router pero solamente dos casos con herramienta exitosa. Se recalculan desde las trazas las métricas separadas de router, solicitud, resultado registrado y éxito en recalculated.json. La run original de W&B no se modifica ni se declara corregida retrospectivamente. El código nuevo separa esos eventos para futuras ejecuciones; **no requiere repetir la inferencia**. W&B terminó según logs; acceso externo/dashboard todavía pendiente.

## Qué sigue

Actualización posterior: [revisión humana recibida](../human_response_review_01/RECEPCION.md). Confirma un fallo crítico nuevo y dos regresiones de invarianza para NF4; se veta su despliegue. Ocho dudas se conservan abiertas y no se inventan notas LLM. El original de la corrida y sus métricas no cambian; esta nota es auditoría documental posterior.

Revisión humana de las [44 respuestas reales](../../eval/review_comparison02/LEEME.md), separada de las doce anclas ya aprobadas; completar calibración/confirmación del juez y evaluar estas mismas respuestas guardadas. Cerrar controles/dominio antes de aceptar eficiencia. La base FP16 es candidata de desarrollo, no producto seguro aprobado. Integración pública M1+RAG+visión, reporte/presentación, reproducción y entrega siguen pendientes. La API del juez y su presupuesto no participaron en esta corrida.

Recalcular localmente sin GPU ni red: `python -m final.comparison02_audit` desde el repositorio, con dependencias de pruebas instaladas.
