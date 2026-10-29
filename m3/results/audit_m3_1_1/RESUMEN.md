# Recálculo posterior de reglas deterministas

No es una nueva corrida del modelo. Respuestas, juez y latencias son los originales.
La cobertura léxica no demuestra verdad semántica. Se aplican las mismas reglas a las seis variantes.

| Variante | Cobertura de hechos | Juez original | Dominio auditado |
|---|---:|---:|---:|
| ablacion_denso_rerank | 0.278 | 3.167 | 3/12 |
| ablacion_solo_hibrido | 0.500 | 3.917 | 3/12 |
| rag_avanzado | 0.500 | 4.000 | 3/12 |
| rag_ingenuo | 0.250 | 3.000 | 3/12 |
| sin_rag | 0.167 | 2.333 | 2/12 |
| sistema_final | 0.611 | 4.167 | 4/12 |

Casos con cambios de evaluación: 2. Detalle: `audit.json`.
RAGAS no se recalculó en este paso. No mezclar su versión original con una nueva sin identificarla.
