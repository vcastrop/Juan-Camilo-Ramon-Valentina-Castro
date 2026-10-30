# Cierre del contraste con la guía M3

Fecha: 29/10/2026. Fuente de requisitos: `STAI_M3_Asignacion_RAG_agentico.pdf`, seis páginas, facilitado por el equipo. Revisión documental asistida por IA; no es una calificación ni una nueva ejecución GPU.

La ruta de reproducción es [RUTA_ENTREGA.md](RUTA_ENTREGA.md). Las verificaciones técnicas previas y sus evidencias están en [REVISION_ENTREGA.md](REVISION_ENTREGA.md).

| Requisito | Ubicación / evidencia | Resultado y salvedades |
|---|---|---|
| Corpus real, fuente, tamaño y licencia | corpus/README.md, documents.jsonl, source_snapshot.json, manifest.json | 24 fichas públicas; revisión humana de privacidad documentada. No son contratos completos. |
| Ingesta, chunking, embeddings y almacenamiento | prepare_corpus.py, ingest.py, indexing/; corrida final | Pipeline ejecutado y reconstrucción CPU auditada; 133 chunks, Chroma. |
| Tres decisiones justificadas para el corpus | README: corpus e indexación | Tamaño/solape, embeddings y top-k explicados. |
| RAG ingenuo conservado | sistemas_m3.py, rag_basic.py | Recuperación densa top-3 y generación, medido como comparación. |
| Válvula de escape | Prompt, campo abstencion y respuestas guardadas | Implementada, pero avanzado/final fallan en los dos casos sin respuesta (0/2). No se declara este comportamiento resuelto. |
| Dos técnicas avanzadas elegidas por diagnóstico | retrieval_advanced.py, README, tablas de ablaciones | Híbrido BM25+denso/RRF y reranking; filtro ID; efecto medido con ablaciones. |
| Herramienta, esquema, JSON tolerante y límite de pasos | contract_tools.py, agent_v5.py, structured_output.py, pruebas | Herramienta numérica con fuentes, agente acotado. Evidencias de dos cálculos y casos sin herramienta; llamada innecesaria en m3_009 reportada. |
| Funciones de sistema con interfaz común | sistemas_m3.py, run_final_m3.py | Sin RAG, ingenuo, avanzado, final y dos ablaciones. |
| Gold de al menos 10 preguntas y 2 no respondibles | eval/gold_v1/eval_set.json y evidencia humana | 12 preguntas, incluidas 2 no respondibles. Nuevas preguntas QA permitidas por la guía para un M1 de clasificación. |
| Harness común y delta limpio | harness_m3.py, harness_m3_v11.py, scorecards y metadata | Mismo gold, generador y prompt base para las seis variantes; tres dimensiones y mediana de latencia. La fila sin RAG es adaptación QA, no ejecución del clasificador RoBERTalex M2. Las métricas se adaptaron a QA y se corrigieron post-hoc: salvedad explícita frente a una lectura literal de «sin cambiar la vara». |
| Cuatro métricas RAGAS y juez identificado | ragas_m3.py, ragas_m3_v11.py, results/final_m3_ragas_v1_1/ | Implementación del laboratorio, juez Qwen2.5-3B, contexto y referencia. Corridas preservadas; no se certifica plena validez: juez degenerado en context precision y omisión de afirmaciones cortas en faithfulness. |
| Frase sencilla, diagrama, tablas y lectura honesta | README.md | Explica qué movió qué, costo, errores de recuperación/generación y fallo de abstención. |
| Semillas, revisiones, Colab gratuito y resultados guardados | Notebooks final/RAGAS 1.1, requirements, metadata, results/ | T4 sin claves pagas; resultados 1.0 y recálculos 1.1 separados. Auditoría CPU posterior, no nueva corrida completa T4. No garantizar identidad entre entornos. |
| Declaración de IA de construcción | README, USO_DE_IA.md | Herramientas, tareas y revisiones humanas declaradas; distinta de los modelos del sistema. |
| Repositorio, PR y envío del enlace | CHECKLIST.md | Cierre operativo separado; no atribuir envío en Interactiva ni fusión sin confirmación. |

## Interpretación del cierre

Están presentes los componentes, las corridas, los resultados y el reporte necesarios para revisar la entrega. Completar este contraste no permite afirmar «100/100»: la abstención falla, RAGAS tiene defectos conocidos y el harness se adaptó respecto de M2. Estas salvedades pueden afectar la evaluación académica y se conservan expresamente, sin cambiar reglas ni regenerar respuestas para mejorar cifras.

El juez alternativo y nuevas correcciones de comportamiento se pospusieron; no se presentan como ejecutados. Los pendientes operativos son publicar el cierre, revisar/aprobar el PR, fusionar si el equipo lo autoriza y entregar el enlace con comprobante.
