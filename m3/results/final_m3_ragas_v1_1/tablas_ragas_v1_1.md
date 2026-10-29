| Sistema | Faithfulness | Answer relevancy | Context precision (lab) | Context recall (lab) | Context precision (rango) | Context recall (segmentos) |
|---|---:|---:|---:|---:|---:|---:|
| RAG ingenuo (S07): denso top-3 | 0.697 (n=11) | 0.501 (n=10) | 0.000 (n=10) | 0.200 (n=10) | 0.033 (n=10) | 0.167 (n=10) |
| RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking | 0.569 (n=12) | 0.317 (n=10) | 0.000 (n=10) | 0.500 (n=10) | 0.350 (n=10) | 0.592 (n=10) |
| Sistema final: avanzado + herramienta (agente acotado) | 0.653 (n=12) | 0.330 (n=10) | 0.000 (n=10) | 0.700 (n=10) | 0.383 (n=10) | 0.792 (n=10) |
