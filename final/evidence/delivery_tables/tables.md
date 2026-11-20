# Tablas reproducibles de la entrega

| Perfil | Cobertura literal | Juez /5 | Dominio /22 | p50 s | p95 s | Pico CUDA GiB |
|---|---:|---:|---:|---:|---:|---:|
| Control QA sin RAG | 0.182 | 3.500 | 3/22 | 2.314 | 6.410 | 5.833 |
| M3 textual | 0.280 | 4.273 | 7/22 | 6.006 | 10.916 | 5.879 |
| Integrado visual FP16 | 0.667 | 4.364 | 16/22 | 7.533 | 13.367 | 10.175 |
| Integrado visual NF4 | 0.530 | 3.773 | 11/22 | 10.750 | 15.155 | 6.349 |
| FP16 sin herramienta | 0.667 | 4.227 | 15/22 | 7.176 | 13.439 | 10.175 |
| Final OCR FP16 (referencia Colab) | 0.712 | 4.455 | 18/22 | 7.045 | 11.926 | No medido |

Cobertura es un diagnóstico, no exactitud. Los cinco perfiles de comparación02
comparten sesión TeslaT4. OCR20 usa otra sesión TeslaT4 y tiempo de pared del
harness, sin control equivalente de calentamiento/sincronización: su latencia
es descriptiva, no evidencia de aceleración. No se midió memoria OCR.
Los perfiles textuales reciben diez imágenes pero se abstienen sin leerlas.
El control sin RAG es adaptación QA, no el clasificador M2 original.
