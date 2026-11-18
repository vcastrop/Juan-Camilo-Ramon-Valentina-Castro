# Mistral con tokenización nativa: ejecución conservada, juez rechazado

Auditoría del 18/11/2026. Código ejecutado: `5b505ce76fc55cbfe9e95df86eb31815dd5fc66d`. El ZIP y notebook originales se conservan sin modificar; sus hashes y verificaciones están en [audit.json](audit.json).

Las 38 generaciones coinciden con la tokenización nativa y tienen un solo BOS inicial. Se recalculó el resumen y coincide con el entregado. No hubo truncamiento; se mantuvieron modelo, rúbrica, anclas, umbrales y perfil de ejecución de la comparación.

| Comprobación | Mistral anterior | Tokenización corregida |
|---|---:|---:|
| Juicios válidos | 38/38 | 38/38 |
| Principales en rango aprobado | 11/20 | 13/20 |
| Respuestas malas con nota 4–5 | 8 | 7 |
| Diferencia máxima de verbosidad mitigada | 3 | 3 |

El filtro exige al menos 18/20, ningún malo con nota alta y diferencia máxima de 1 en los seis pares. **No pasó**. Entre los fallos persisten el número incorrecto (4), el conflicto ignorado (5) y la explicación vacía (5). La negación sí recibe ahora 1. No se corrige ninguna nota ni se seleccionan solo mejoras.

La corrección de entrada era necesaria, pero no bastó para obtener buen juicio. Esta comparación no demuestra que la cuantización sea la causa del fallo ni valida al juez para medir eficiencia. La run W&B `g2ws2xv0` finalizó según los logs; acceso al dashboard no verificado.

Siguiente candidato: [protocolo por criterios con razonamiento](../../JUEZ_RAZONAMIENTO.md). Las corridas anteriores permanecen como evidencia negativa.
