| Sistema | Dim. 1 exactitud (0-1) | Dim. 2 juez (1-5, válidos) | Dim. 3 dominio | Latencia mediana (s) |
|---|---:|---:|---:|---:|
| Línea base sin RAG (mismo generador; adaptación de M2) | 0.167 | 2.333 (12/12) | 2/12 (0.167) | 6.72 |
| RAG ingenuo (S07): denso top-3 | 0.250 | 3 (12/12) | 3/12 (0.250) | 8.00 |
| RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking | 0.500 | 4 (12/12) | 4/12 (0.333) | 8.37 |
| Sistema final: avanzado + herramienta (agente acotado) | 0.611 | 4.167 (12/12) | 5/12 (0.417) | 8.86 |
| Ablación: híbrido RRF con filtro de ID, sin reranking | 0.500 | 3.917 (12/12) | 3/12 (0.250) | 7.61 |
| Ablación: denso + reranking, sin híbrido | 0.278 | 3.167 (12/12) | 3/12 (0.250) | 7.94 |

| Sistema | Faithfulness | Answer relevancy | Context precision | Context recall | Fuente gold recuperada |
|---|---:|---:|---:|---:|---:|
| RAG ingenuo (S07): denso top-3 | 0.642 (n=11) | 0.501 (n=10) | 0.033 (n=10) | 0.167 (n=10) | 0.200 |
| RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking | 0.644 (n=12) | 0.317 (n=10) | 0.350 (n=10) | 0.592 (n=10) | 1.000 |
| Sistema final: avanzado + herramienta (agente acotado) | 0.708 (n=12) | 0.330 (n=10) | 0.383 (n=10) | 0.792 (n=10) | 1.000 |
