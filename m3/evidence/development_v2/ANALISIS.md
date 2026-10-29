# Comparación de desarrollo v2 — evidencia, no evaluación final

Corrida iniciada el 29/10/2026 03:10:11 UTC (28/10, 22:10 Colombia), Tesla T4, semilla 42. Artefactos originales aportados por el equipo:

- [Resultados originales](contractrisk_m3_desarrollo_v2_resultados.zip): metadata.json, predictions.jsonl y chunks.jsonl.
- [Notebook ejecutado](ContractRisk_M3_Desarrollo_v2_Colab_Ejecutado.ipynb): cuatro celdas de código ejecutadas, sin outputs de tipo error.

Metadata declara completed y development_v2_not_final_scorecard. Se verificaron los hashes de los nueve archivos Python contra el ZIP de código entregado; todos coinciden. Los 133 chunks coinciden con las posiciones del corpus original. Los contextos de las predicciones coinciden con esos chunks. No se alteraron respuestas, referencias ni resultados.

## Comparación observada

Cuatro preguntas de desarrollo sobre modalidad, separadas del gold final. Los aciertos se determinaron revisando respuesta y evidencia, no por un juez LLM. Cada variante añade una prueba sintética sin contexto, excluida de la tabla y de las medianas.

| Variante | Contrato correcto recuperado | Fragmento con modalidad | Respuestas correctas | Mediana extremo a extremo (s) |
|---|---:|---:|---:|---:|
| dense_v2 | 0/4 | 0/4 | 0/4 | 4.528 |
| hybrid_idfilter_v2 | 4/4 | 3/4 | 3/4 | 2.957 |
| hybrid_idfilter_rerank_v2 | 4/4 | 4/4 | 3/4 | 3.456 |

Las tres variantes comparten generador Qwen2.5-1.5B-Instruct, prompt v2, top-k 3, corpus y fragmentación de 220 caracteres/30 de solapamiento. Híbrido usa BM25+denso+RRF y filtro por identificador explícito; reranking usa cross-encoder sobre hasta 12 candidatos. Revisiones exactas, versiones efectivas y hashes están en metadata.json. No se atribuye al híbrido aislado lo que también depende del filtro de ID.

## Diagnóstico por caso

- Denso: no recupera los contratos solicitados; responde duraciones como si fueran modalidades. Citar un chunk existente y emitir JSON válido no demuestra sustento.
- Híbrido, CO1.PCCNTR.1180445: trae el contrato correcto pero no el fragmento de modalidad; responde con el objeto. Fallan selección de contexto y abstención del generador.
- Reranking, CO1.PCCNTR.1180445: recupera c003 con Mínima cuantía y responde correctamente. Mejora observable de selección.
- Reranking, CO1.PCCNTR.3156756: c003 contiene tanto Tipo de contrato: Compraventa como Modalidad de contratación: Contratación directa. El generador responde Compraventa. Es un error de interpretación pese a disponer de la evidencia. El híbrido sí acertó este caso.
- Los otros dos contratos, CO1.PCCNTR.1637043 y CO1.PCCNTR.5484069, se responden correctamente en ambas variantes avanzadas, con citas a los fragmentos pertinentes.

## Formato y abstención

15/15 salidas estructuralmente válidas. Cada variante se abstuvo en la prueba deliberadamente sin contexto. Esto NO valida abstención cuando hay contexto irrelevante: el denso demuestra lo contrario. No hubo corrección automática de abstencion ni selección de respuestas por mejor puntuación.

## Límites y decisiones siguientes

Cuatro preguntas del mismo tipo con IDs explícitos no prueban generalización, cálculo, herramientas ni comportamiento sobre gold. Latencias descriptivas de una corrida, sin repetición estadística ni separación de calentamiento; menor latencia total del híbrido no demuestra menor costo de recuperación, pues la longitud de generación varía. La comparación con smoke v1 cambia también prompt y fragmentación: no es una ablación controlada entre versiones.

Conservar ambas técnicas para la comparación prevista sin declarar superioridad final. Reforzar distinción entre campos y abstención con desarrollo separado; versionar cualquier nuevo prompt común. Pendientes: agente/herramienta, juez independiente calibrado, dominio, RAGAS y cuatro variantes sobre gold. No sustituir ni modificar el gold humano para mejorar estos resultados.
