# Comparación 01: recolección sin depender de la API del juez

Estado 18/11/2026: código preparado y probado en CPU con dobles de prueba. **Sin ejecución real de estos perfiles todavía.** No se cambian M1–M3 históricos, main ni Space. [Notebook T4](ContractRisk_Final_Comparacion_01_Colab.ipynb).

## Qué ejecuta

22 entradas comunes × cinco perfiles = 110 filas si termina. Incluye 12 preguntas textuales y 10 imágenes; las referencias no se envían al modelo. Se reutilizan las entradas aprobadas, **no** las respuestas de ensayos anteriores.

| Perfil | Implementación y límites |
|---|---|
| qa_no_rag_fp16 | `sin_rag` de M3 con retrieve=False; adaptación QA de la línea base, no reclasificación M2 ni comparación directa con su Macro F1. No recibe imágenes ni transcripciones. |
| m3_text_fp16 | `sistema_final` reconstruido con la fábrica histórica M3 y su codificación de chat original; corpus/fragmentación/modelos fijos. No recibe imágenes. Nueva ejecución, no reemplazo de resultados M3. |
| integrated_fp16 | Integración visual 0.3, registros completos recuperados, política de herramienta y control de contradicciones. Generador con codificación nativa de chat comprobada. Nueva base, no idéntica a visual03. |
| integrated_nf4 | Igual a integrated_fp16 salvo pesos NF4 del generador, doble cuantización y cómputo FP16. VLM sigue FP16. Sin fallback silencioso ni cuantización del juez. |
| integrated_no_tool_fp16 | Misma integración FP16 pero desactiva solo la herramienta/router; responde mediante el mismo protocolo RAG. Ablación que mide el aporte conjunto de la ruta de herramienta. |

Los perfiles textuales declaran abstención por imagen no soportada y permanecen en el denominador. Se informa resumen separado por modalidad para no ocultar que sus respuestas a imágenes son rápidas y no contienen inferencia visual. La tabla evolutiva cambia varios componentes entre etapas; no atribuir toda diferencia a una técnica aislada. La ablación y la pareja de precisión sí delimitan cambios concretos.

El clasificador M1 no se carga en este benchmark de QA: medirlo contra respuestas QA sería inválido. Su integración visible y prueba pública siguen pendientes y no se declaran completadas por este notebook.

## Medición y trazabilidad

- Una pasada por perfil, orden fijado antes de ejecutar. Semilla 42, modelos/revisiones fijados, generación greedy y 512 tokens. No hay selección de mejores notas, retries semánticos o caché de respuestas.
- Embeddings y reranker en CPU. En los perfiles visuales, VLM y generador residentes simultáneamente en GPU. Clasificador excluido de todos estos perfiles.
- Calentamientos de pregunta genérica e imagen ficticia, excluidos y guardados; carga/descarga separada de tiempos por solicitud.
- Sincronización CUDA antes/después y reinicio de picos por caso. Memoria pico asignada del proceso completo y reservada por separado, bytes. p50/p95 descriptivos; sin repeticiones ni orden contrabalanceado no se promete estabilidad universal de latencia.
- Se guardan respuestas, contextos, intentos, herramientas, lectura visual, errores por tipo, picos y tiempos; fallos no se eliminan. OOM/error de medición conserva parcial y detiene el proceso.
- W&B registra métricas numéricas por perfil, no preguntas, imágenes, OCR ni respuestas. La evidencia detallada usa solo el paquete público/revisado del proyecto y se descarga en ZIP.
- Hashes de código, entradas, referencias, corpus, reglas, paquetes y configuración. El soporte de NF4 está documentado, pero compatibilidad real de esta combinación se comprobará en Colab, no se presupone por tests CPU. [Transformers](https://huggingface.co/docs/transformers/v4.57.0/quantization/bitsandbytes), [versión fijada](https://pypi.org/project/bitsandbytes/0.50.2/), consultados 18/11/2026.

## Evaluación no completada

Las [reglas de dominio y controles](domain_protocol_v1.json) se predeclaran antes de esta comparación y su hash se guarda con la corrida. Se exige respaldo de respuesta y explicación, completitud, citas exactas, abstención correcta, juez validado >=4 y ausencia de fallos críticos auditados. No es otro nombre para cobertura literal.

El evaluador CPU conserva sus diagnósticos literales como tales; `domain_pass`, cumplimiento y notas del juez permanecen pendientes. Falta conectar la validación del juez y las decisiones semánticas/daño con evidencia real. No se acepta eficiencia a partir de proxies. No se cambian reglas al ver respuestas para hacer pasar la cuantización; una modificación requerirá versión explícita y recalificación consistente de todas las filas.

La revisión humana de los doce ejemplos separados está [cerrada](evidence/confirmation_review_01/CIERRE.md); su ejecución y la validación del juez no. Gemini no participa en esta recolección y el presupuesto Drive no se abre ni modifica.

## Instrucciones al equipo

1. Abrir notebook Comparación 01 en Colab con sesión nueva **GPU T4**; cerrar otros procesos/modelos de esa sesión.
2. Dar acceso únicamente al secreto existente WANDB_API_KEY. No requiere GEMINI_API_KEY ni nueva cuenta o facturación.
3. Ejecutar en orden. No interpretar las pruebas CPU como ejecución de modelos. Si se detiene, conservar el parcial y ejecutar inspección/descarga.
4. Descargar `contractrisk_final_comparacion01_resultados.zip` y el notebook con sus salidas; enviar ambos. No guardar directamente sobre main desde Colab.
5. Auditar hashes, casos, mediciones y respuestas; después completar calificación semántica y decidir aceptación con la política previa. M1, producción, reporte y presentación siguen como hitos separados.
