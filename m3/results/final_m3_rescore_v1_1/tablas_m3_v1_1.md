| Sistema | Dim. 1 cobertura de hechos (0-1) | Respuestas con cobertura completa | Dim. 2 juez (1-5) | Dim. 3 chequeo de dominio | Latencia mediana (s) |
|---|---:|---:|---:|---:|---:|
| Línea base sin RAG (mismo generador; adaptación de M2) | 0.167 | 2/12 | 2.33 | 2/12 | 6.72 |
| RAG ingenuo (S07): denso top-3 | 0.250 | 3/12 | 3 | 3/12 | 8.00 |
| RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking | 0.500 | 4/12 | 4 | 3/12 | 8.37 |
| Sistema final: avanzado + herramienta (agente acotado) | 0.611 | 5/12 | 4.17 | 4/12 | 8.86 |
| Ablación: híbrido RRF con filtro de ID, sin reranking | 0.500 | 3/12 | 3.92 | 3/12 | 7.61 |
| Ablación: denso + reranking, sin híbrido | 0.278 | 3/12 | 3.17 | 3/12 | 7.94 |

| Sistema | Hechos requeridos en fragmentos recuperados (media) | Casos con todos los hechos recuperados | Con resultado de herramienta |
|---|---:|---:|---:|
| Línea base sin RAG (mismo generador; adaptación de M2) | 0.000 | 0/10 | 0/10 |
| RAG ingenuo (S07): denso top-3 | 0.200 | 2/10 | 2/10 |
| RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking | 0.700 | 6/10 | 6/10 |
| Sistema final: avanzado + herramienta (agente acotado) | 0.700 | 6/10 | 8/10 |
| Ablación: híbrido RRF con filtro de ID, sin reranking | 0.650 | 5/10 | 5/10 |
| Ablación: denso + reranking, sin híbrido | 0.300 | 2/10 | 2/10 |
