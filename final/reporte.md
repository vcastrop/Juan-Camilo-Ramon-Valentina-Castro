# ContractRisk Colombia — borrador de reporte integrador

**Estado: BORRADOR EN DESARROLLO, no entrega cerrada.** Recolección y 110 notas LLM auditadas; juez aceptado para esta tarea tras calibración, confirmación y revisión humana. Dominio cerrado para FP16/NF4 y eficiencia NF4 rechazada con evidencia. Quedan 46 revisiones semánticas de otros perfiles, despliegue contractual real, atribución final de tareas, presentación y reproducción completa. No se presentan pendientes como resultados completos.

## Problema, usuario y alcance

ContractRisk apoya a una persona analista que consulta fichas públicas contractuales. Integra una señal de suficiencia descriptiva de M1, recuperación y herramientas de M3 y lectura de representaciones visuales de fichas. No detecta ni determina fraude. Un monto, una fecha o un estado contractual no prueban irregularidad o cumplimiento físico.

La decisión apoyada es si existe evidencia suficiente y trazable para responder la consulta o si se requiere revisar fuentes/documentos adicionales. El éxito se evalúa por respuesta sustentada y completa, explicación/citas verificables y abstención adecuada. En los dos perfiles con revisión semántica cerrada: 16/22 en FP16 y 11/22 en NF4. No se sustituyen por coincidencia literal ni se generalizan a uso real.

## Arquitectura y procedencia

Pregunta y, opcionalmente, imagen → extracción visual y campos → recuperación híbrida con filtro de ID y reranking → fuentes completas y herramienta numérica cuando corresponde → respuesta estructurada con citas o abstención. El control de consistencia compara lectura visual/snapshot e informa discrepancias sin afirmar autenticidad. M1 tiene un modo separado de suficiencia; su integración pública visible sigue pendiente.

La base histórica M1–M3 se conserva. No existía una entrega M4/M5 externa publicada: la integración visual y el experimento de eficiencia son desarrollos nuevos. Las fichas visuales son representaciones sintéticas de datos del snapshot, no contratos firmados. Los resultados originales y sus fallos no se reescriben.

## Diseño de evaluación y reproducibilidad

Conjunto común: 22 entradas (12 textuales y 10 visuales), derivadas de referencias revisadas y ya inspeccionadas durante desarrollo; no son 22 contratos independientes ni gold ciego. Se separan entradas y referencias. Se incluyen falta de datos, cláusulas/auditoría ausentes, instrucción adversarial rotulada, imagen blanca y pares de contraste/rotación.

Tres dimensiones: cobertura automática literal como diagnóstico, juicio LLM de respaldo y chequeo de dominio con reglas/controles explícitos. [Protocolo registrado](domain_protocol_v1.json). Se conservan notas crudas, sin reemplazarlas por aciertos. Tras candidatos locales rechazados e interrupciones API, Gemini 4 Hydrogen obtuvo 20/20 orientaciones de calibración y 12/12 en confirmación separada, sin respuestas malas aceptadas con 4–5. Los motivos fueron revisados por Juan Camilo, con aceptación condicionada comprobada contra la rúbrica original y límites expresos. [Cierre humano](evidence/human_closure_19/RECEPCION.md), [rúbrica legible](RUBRICA_JUEZ_FINAL.md).

En los seis pares sintéticos, la diferencia media por repetición pasó de 0,5 a 0 tras la mitigación. Se repite una frase cuatro veces: no es prueba de neutralidad ante explicaciones largas legítimas, ni mide fluidez o calidad editorial. El juez no es infalible: conserva notas altas en casos que la revisión humana rechaza; el dominio aplica ambos controles sin modificar la nota cruda. La implementación del cruce es posterior a las corridas y adjudicaciones, no una prueba ciega o prospectiva del evaluador.

Comparación 02: cinco perfiles, 110 registros, cero excepciones de caso y siete salidas inválidas de la base sin RAG, incluidas en el denominador. Tesla T4, mismo conjunto, revisiones de modelos fijadas, torch 2.14.1+cu130 y generación greedy. Carga/calentamiento se separan de inferencia; una pasada ordenada por perfil no garantiza estabilidad general de latencia. [Auditoría y recálculo](evidence/comparison_02/ANALISIS.md).

## Resultados medidos y estado del scorecard

| Perfil | Cobertura literal media | Chequeos automáticos /22 | p50 s | p95 s | Pico CUDA asignado GiB |
|---|---:|---:|---:|---:|---:|
| Sin RAG adaptado a QA | 0,182 | 4 | 2,314 | 6,410 | 5,833 |
| M3 textual reejecutado | 0,280 | 4 | 6,006 | 10,916 | 5,879 |
| Integrado FP16 | 0,667 | 13 | 7,533 | 13,367 | 10,175 |
| Integrado NF4 | 0,530 | 6 | 10,750 | 15,155 | 6,349 |
| Integrado FP16 sin herramienta | 0,667 | 13 | 7,176 | 13,439 | 10,175 |

**No leer cobertura como accuracy ni chequeos como cumplimiento del dominio.** Los perfiles textuales no ven imágenes y sus abstenciones por falta de soporte siguen contando; el ZIP informa también por modalidad. No mezclar Macro F1 de clasificación M2 con estas métricas QA. Las nuevas tablas no reemplazan ni renombran las históricas M3.

La [evaluación 14](evidence/product_14/ANALISIS.md) aplicó el juez validado a las 110 respuestas guardadas, sin regenerar sistemas ni recibir gold. Recalculado desde las notas originales:

| Perfil | Juez /5 global | Texto /5 (12) | Imagen /5 (10) | Dominio |
|---|---:|---:|---:|---:|
| Sin RAG | 3,500 | 2,250 | 5,000 | Pendiente |
| M3 textual | 4,273 | 3,667 | 5,000 | Pendiente |
| Integrado FP16 | 4,364 | 4,167 | 4,600 | 16/22 (72,73 %) |
| Integrado NF4 | 3,773 | 4,083 | 3,400 | 11/22 (50,00 %) |
| Integrado FP16 sin herramienta | 4,227 | 3,917 | 4,600 | Pendiente |

**La nota del juez no equivale a resolver la tarea.** Los perfiles textuales obtienen 5 por abstenerse honestamente ante imágenes que no pueden procesar; no son diez tareas visuales resueltas. El juez recibe texto/evidencia registrada, no los píxeles, y puede premiar una lectura visual equivocada o una justificación que un humano rechaza. FP16 m3_006 recibe 4 pese a respaldo humano NO, y vis_05 recibe 5 pese a explicación humana NO; NF4 m3_006 recibe 4 pese a respaldo humano NO. Se conservan esas discrepancias y el dominio falla: no se corrigen notas para hacerlas coincidir.

El dominio completo de la pareja usa 44 anotaciones reales y el cierre de once criterios de ocho dudas. Otras veinte anotaciones se transfieren a la ablación por igualdad comprobada del mismo caso, respuesta y payload de evidencia, sin afirmar una nueva revisión humana. Quedan 46 salidas distintas sin auditoría semántica cerrada; sus tasas son pendientes/null, no cero. [Recálculo JSON](evidence/product_14/scorecard_derived.json) y [CSV](evidence/product_14/scorecard_derived.csv).

NF4 verificó 252 capas de cuatro bits y redujo la memoria pico un 37,60 %, pero fue un 42,70 % más lenta en mediana en esta pasada. Con umbrales aprobados antes de medir (≤5 puntos de pérdida de dominio, cero fallos críticos nuevos/retrocesos de controles y ≥20 % menos memoria), el resultado ahora es **rechazado**: pierde 22,73 puntos de dominio, introduce un fallo crítico en m3_001 y dos regresiones de invarianza. Solo pasa el ahorro de memoria. La resistencia a la instrucción adversarial pasa en ambos; la omisión de monto de NF4 en ese caso falla completitud, no demuestra obediencia a la inyección. NF4 no se selecciona para despliegue; FP16 conserva seis fallos de dominio y no queda certificado para decisiones reales.

En la ablación, ambas respuestas cortas de cálculo son correctas con y sin herramienta; no se demuestra mejora de esa exactitud. Sin herramienta, la explicación de m3_007 escribe 16.800.000 frente a 168.000.000 en la respuesta. Con herramienta muestra `abs(250000000 - 82000000)` y el valor correcto. El juez asigna 2 frente a 5; m3_008 obtiene 5 en ambas. La diferencia global es 3/22 = 0,13636 puntos y hay veinte salidas idénticas: evidencia local de explicación más trazable, no mejora universal. [Fallos históricos](evidence/comparison_02/ANALISIS.md) y [auditoría actual](evidence/product_14/ANALISIS.md).

## Producción y observabilidad: estado pendiente

Space objetivo: https://huggingface.co/spaces/Juanoff/contractrisk-colombia. La versión pública comprobada es de infraestructura; no afirmar que ejecuta aún el sistema contractual completo. W&B registra pruebas de infraestructura y Colab: https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final. Falta comprobar acceso del evaluador y peticiones reales de producción.

El contador histórico tool_used confundió router con herramienta; su fe de erratas y recálculo están documentados sin alterar la run original. Falta verificar arranque frío, salud/listo, límites de entrada/concurrencia, manejo de errores y logs sanitizados del servicio contractual público.

## Ética y límites — borrador breve

Las imágenes con cifras y las preguntas de varios campos muestran riesgo: una lectura añadió un cero y NF4 omitió montos. No medimos representatividad poblacional ni equidad entre entidades; no se puede generalizar desde 22 entradas relacionadas. Datos y representaciones de evaluación revisados se conservan como evidencia; el despliegue todavía debe comprobar su política de retención y conocimiento del usuario antes de recibir contenido nuevo. Una respuesta falsa puede orientar mal una revisión contractual: se requieren citas, controles de contradicción, abstención y decisión humana, sin acusaciones automáticas. Esos controles reducen riesgo, no certifican seguridad.

## Contribuciones humanas y uso de IA — por completar con el equipo

Juan Camilo realizó revisiones humanas de conjuntos/rangos, 44 respuestas, cierre de ocho dudas y motivos de calibración/confirmación, con originales conservados. Las demás contribuciones y las de Valentina deben confirmarse antes de atribuirlas. La IA apoyó código, pruebas, auditoría técnica, el cruce reproducible y este borrador; la lectura técnica de los 110 motivos no se presenta como revisión humana. No se inventan ejecuciones, notas o resultados.

## Cierre pendiente

Revisión humana original de 18/11/2026 y [cierre firmado de 19/11](evidence/human_closure_19/RECEPCION.md) conservados por separado. Evaluación 14 completa en su dimensión LLM; dominio/eficiencia cerrados para la pareja FP16/NF4, no para todos los perfiles. La decisión relativa de NF4 es rechazo, sin aprobar globalmente FP16. El acumulado USD 5,7954525 estimado/reservado queda dentro de USD 7 totales autorizados; no se presenta como factura y no se liberan reservas desconocidas.

- Cerrar 46 revisiones semánticas pendientes para las tasas de dominio de otros perfiles; conservar discrepancias con el juez.
- Preparar configuración viable a partir de FP16 y verificar sus fallos, sin desplegar NF4 ni cambiar umbrales para aprobarla.
- Publicar y probar sistema contractual real y observabilidad accesible.
- Completar portada, diagrama final, enlaces de reproducción, tareas reales por integrante y diapositivas.
- Reproducir desde limpio, comprobar tablas/accesos/privacidad/licencias, PR y merge autorizados, entrega y comprobante.

Ver [checklist](CHECKLIST.md) y [progreso](PROGRESO_FINAL.md). No declarar 100 % hasta cerrar los hitos con evidencias.
