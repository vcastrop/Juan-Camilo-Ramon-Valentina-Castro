# Diagnóstico de la primera corrida real de RAG

Archivo original entregado por el usuario: `contractrisk_m3_smoke_resultados_sqlite.zip`, preservado en esta carpeta. No se reemplazan ni corrigen sus respuestas.

- Ejecución completada en Tesla T4, Python 3.13.16. Inicio registrado: 2026-10-29T02:56:47.578231+00:00.
- El primer intento anterior había fallado por ausencia de SQLite FTS5. El usuario aplicó pysqlite3-binary en el subproceso y esta corrida terminó. Su metadata antigua no registra el backend SQLite; no se agrega retrospectivamente como si lo hubiera registrado.
- Cuatro preguntas de desarrollo, cuatro JSON sintácticamente válidos, cero respuestas aceptadas por el validador.
- Ningún top-3 contiene un fragmento del contrato preguntado (0/4). Las cuatro referencias sí se encuentran en las fichas del corpus.
- Las cuatro salidas expresan falta de información, pero declaran `abstencion=false` con citas vacías. El error reportado es de contrato de salida, no de sintaxis JSON.
- Latencia mediana registrada: 3.8851451709999765 segundos. Muestra muy pequeña, sin benchmark de rendimiento ni control de calentamiento.
- Los fragmentos recuperados coinciden con el texto y offsets del corpus: no se detectó corrupción de las fuentes.

## Hipótesis y siguiente experimento

La búsqueda densa no está discriminando los IDs exactos. Además, muchos fragmentos no contienen el identificador de su ficha en el texto embebido. Estas observaciones motivan incorporar el ID como metadato textual para todos los buscadores de la nueva comparación, BM25 + dense con RRF, filtro por IDs explícitamente escritos en la pregunta y reranking con cross-encoder.

El filtro por ID es una decisión adicional, distinta de BM25/RRF y de reranking. Se declarará como tal. La diferencia entre híbrido y híbrido+reranker sí permite estudiar el efecto incremental del reranker; la diferencia frente a la corrida antigua no aísla una sola técnica porque también cambia el prompt y la preparación de fragmentos. No se afirmará que una técnica mejoró nada hasta ejecutar el experimento.

Se conserva el prompt v1. La nueva corrida usa el mismo prompt v2 en las tres variantes y no cambia respuestas históricas ni flexibiliza el validador. Una prueba adicional con contexto vacío comprueba coherencia de abstención y se reporta separada de las preguntas sobre contratos.

Esta corrida y la siguiente son desarrollo. No son el scorecard final, no usan el gold final, no incluyen aún juez/RAGAS ni herramienta agéntica.

Referencias de implementación: [rank_bm25](https://github.com/dorianbrown/rank_bm25), [cross-encoder del curso](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1), [SQLite FTS5](https://www.sqlite.org/fts5.html).
