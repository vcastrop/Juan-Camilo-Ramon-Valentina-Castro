# ContractRisk Colombia — borrador de reporte integrador

**Estado: BORRADOR EN DESARROLLO, no entrega cerrada.** Los resultados de recolección están auditados; faltan evaluación semántica/juez validado, despliegue contractual real, atribución final de tareas, presentación y reproducción completa. No se presentan notas inexistentes como evidencia.

## Problema, usuario y alcance

ContractRisk apoya a una persona analista que consulta fichas públicas contractuales. Integra una señal de suficiencia descriptiva de M1, recuperación y herramientas de M3 y lectura de representaciones visuales de fichas. No detecta ni determina fraude. Un monto, una fecha o un estado contractual no prueban irregularidad o cumplimiento físico.

La decisión apoyada es si existe evidencia suficiente y trazable para responder la consulta o si se requiere revisar fuentes/documentos adicionales. El éxito previsto se evalúa por respuesta sustentada y completa, explicación/citas verificables y abstención adecuada; su tasa final sigue pendiente, no se sustituye por coincidencia literal.

## Arquitectura y procedencia

Pregunta y, opcionalmente, imagen → extracción visual y campos → recuperación híbrida con filtro de ID y reranking → fuentes completas y herramienta numérica cuando corresponde → respuesta estructurada con citas o abstención. El control de consistencia compara lectura visual/snapshot e informa discrepancias sin afirmar autenticidad. M1 tiene un modo separado de suficiencia; su integración pública visible sigue pendiente.

La base histórica M1–M3 se conserva. No existía una entrega M4/M5 externa publicada: la integración visual y el experimento de eficiencia son desarrollos nuevos. Las fichas visuales son representaciones sintéticas de datos del snapshot, no contratos firmados. Los resultados originales y sus fallos no se reescriben.

## Diseño de evaluación y reproducibilidad

Conjunto común: 22 entradas (12 textuales y 10 visuales), derivadas de referencias revisadas y ya inspeccionadas durante desarrollo; no son 22 contratos independientes ni gold ciego. Se separan entradas y referencias. Se incluyen falta de datos, cláusulas/auditoría ausentes, instrucción adversarial rotulada, imagen blanca y pares de contraste/rotación.

Tres dimensiones previstas: cobertura automática literal como diagnóstico, juicio LLM de respaldo y chequeo de dominio con reglas/controles explícitos. [Protocolo predeclarado](domain_protocol_v1.json). Las dos últimas no se completan por obtener JSON válido: el juez debe superar calibración y confirmación; se conservan notas crudas, sin reemplazarlas por aciertos. Jueces locales anteriores fallaron criterios; API produjo una nota válida y posteriores interrupciones. No hay juez validado todavía.

Comparación 02: cinco perfiles, 110 registros, cero excepciones de caso y siete salidas inválidas de la base sin RAG, incluidas en el denominador. Tesla T4, mismo conjunto, revisiones de modelos fijadas, torch 2.14.1+cu130 y generación greedy. Carga/calentamiento se separan de inferencia; una pasada ordenada por perfil no garantiza estabilidad general de latencia. [Auditoría y recálculo](evidence/comparison_02/ANALISIS.md).

## Resultados medidos, no scorecard semántico final

| Perfil | Cobertura literal media | Chequeos automáticos /22 | p50 s | p95 s | Pico CUDA asignado GiB |
|---|---:|---:|---:|---:|---:|
| Sin RAG adaptado a QA | 0,182 | 4 | 2,314 | 6,410 | 5,833 |
| M3 textual reejecutado | 0,280 | 4 | 6,006 | 10,916 | 5,879 |
| Integrado FP16 | 0,667 | 13 | 7,533 | 13,367 | 10,175 |
| Integrado NF4 | 0,530 | 6 | 10,750 | 15,155 | 6,349 |
| Integrado FP16 sin herramienta | 0,667 | 13 | 7,176 | 13,439 | 10,175 |

**No leer cobertura como accuracy ni chequeos como cumplimiento del dominio.** Los perfiles textuales no ven imágenes y sus abstenciones por falta de soporte siguen contando; el ZIP informa también por modalidad. No mezclar Macro F1 de clasificación M2 con estas métricas QA. Las nuevas tablas no reemplazan ni renombran las históricas M3.

NF4 verificó 252 capas de cuatro bits y redujo la memoria pico un 37,6 %, pero fue un 42,7 % más lenta en mediana en esta pasada y omitió montos en varias respuestas visuales. Los umbrales previos exigen ≤5 puntos de pérdida de dominio, cero fallos críticos nuevos/retrocesos de controles y ≥20 % menos memoria. Solo la condición de memoria puede darse por comprobada; la aceptación integral permanece no evaluable. NF4 no está aceptada para despliegue.

En la ablación, ambos cálculos resultaron correctos con y sin herramienta. La herramienta aporta ejecución trazable; no se demuestra mejora de exactitud en esta muestra. FP16 y la ablación coinciden en otras veinte salidas. [Fallos reales y límites de interpretación](evidence/comparison_02/ANALISIS.md).

## Producción y observabilidad: estado pendiente

Space objetivo: https://huggingface.co/spaces/Juanoff/contractrisk-colombia. La versión pública comprobada es de infraestructura; no afirmar que ejecuta aún el sistema contractual completo. W&B registra pruebas de infraestructura y Colab: https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final. Falta comprobar acceso del evaluador y peticiones reales de producción.

El contador histórico tool_used confundió router con herramienta; su fe de erratas y recálculo están documentados sin alterar la run original. Falta verificar arranque frío, salud/listo, límites de entrada/concurrencia, manejo de errores y logs sanitizados del servicio contractual público.

## Ética y límites — borrador breve

Las imágenes con cifras y las preguntas de varios campos muestran riesgo: una lectura añadió un cero y NF4 omitió montos. No medimos representatividad poblacional ni equidad entre entidades; no se puede generalizar desde 22 entradas relacionadas. Datos y representaciones de evaluación revisados se conservan como evidencia; el despliegue todavía debe comprobar su política de retención y conocimiento del usuario antes de recibir contenido nuevo. Una respuesta falsa puede orientar mal una revisión contractual: se requieren citas, controles de contradicción, abstención y decisión humana, sin acusaciones automáticas. Esos controles reducen riesgo, no certifican seguridad.

## Contribuciones humanas y uso de IA — por completar con el equipo

Juan Camilo realizó revisiones humanas de los conjuntos y rangos registradas con originales/confirmaciones; revisión de respuestas reales en curso. Las demás contribuciones y las de Valentina deben confirmarse antes de atribuirlas. La IA apoyó código, pruebas, auditoría técnica y este borrador; no se presentan sus observaciones como revisión humana ni se inventan ejecuciones, notas o resultados.

## Cierre pendiente

- Completar revisión semántica de respuestas y evaluación LLM validada, con discrepancias y límites explícitos.
- Decidir configuración viable según calidad/seguridad y eficiencia, sin modificar umbrales para aprobarla.
- Publicar y probar sistema contractual real y observabilidad accesible.
- Completar portada, diagrama final, enlaces de reproducción, tareas reales por integrante y diapositivas.
- Reproducir desde limpio, comprobar tablas/accesos/privacidad/licencias, PR y merge autorizados, entrega y comprobante.

Ver [checklist](CHECKLIST.md) y [progreso](PROGRESO_FINAL.md). No declarar 100 % hasta cerrar los hitos con evidencias.
