# Auditoría de RAGAS 1.1 sobre las respuestas guardadas de la corrida final

Fecha: 29/10/2026. Revisión técnica asistida por Claude Code, pendiente de revisión humana del equipo.

## Integridad

- Colab Tesla T4, 21:46–21:50 UTC, `status: completed`, código `1575907` (`commit.txt`); 86 pruebas aprobadas (`tests.log`).
- Fuente: `../final_m3/harness_rows.jsonl`, sha256 `0966955b…306e`, igual al archivo del repositorio. No se regeneraron respuestas (`regenerated_answers: false`).
- 36 casos, 393 llamadas al juez, 0 respuestas sí/no sin parsear.
- **Reproducibilidad:** answer relevancy, context precision por rango y context recall por segmentos usan los mismos prompts que la 1.0 y dieron valores **idénticos en los 36 casos**. Con decodificación greedy, el juez es determinista entre sesiones.

## Hallazgos

1. **La context precision del laboratorio no informa nada.** Con el prompt exacto de S10 («¿Este pasaje es relevante para responderla?»), el juez respondió «No» a los 94 pasajes, incluidos los que contienen literalmente la entidad o la modalidad pedidas (por ejemplo, el chunk `Entidad: AEROCIVIL` para m3_002). El 0,000 refleja un juez degenerado para ese prompt, no la calidad de la recuperación.
2. **El context recall del laboratorio sí es coherente con la evidencia.** Coincide con el diagnóstico determinista de `m3-harness-1.1` («todos los hechos requeridos en lo entregado al generador») en 28/30 casos. Los 2 desacuerdos (m3_002, avanzado y final) son falsos negativos del juez: los hechos sí están en el contexto.
3. **Corregir la segmentación cambia faithfulness en 11 casos** y altera el orden entre filas: el ingenuo pasa de 0,642 a 0,697, el avanzado de 0,644 a 0,569 y el final de 0,708 a 0,653. La «mejora» de faithfulness que mostraba 1.0 desaparece. En la 1.1, la auditoría inventada (m3_012) recibe 0,0, como corresponde. Pero el juez también da 0,0 a la explicación de m3_007 del final, aunque la cifra está en el resultado de la herramienta. Faithfulness sigue sin servir para comparar filas.
4. **El filtro de afirmaciones cortas (12 caracteres o menos) dejó fuera la respuesta central en 6 casos**: «5687267» (ingenuo m3_007), «5147» (avanzado m3_007), «15387424 COP» (final m3_008) y «No» (m3_009 en las tres filas). Faithfulness de esos casos solo juzgó la explicación. Es una limitación conservada de 1.1 (ver la tabla «Qué comprueban y qué no» del README).
5. El parser de sí/no lee solo la primera palabra; en esta corrida las 363 respuestas fueron limpias («Sí», «No», «No.», «sí»), así que la ambigüedad no afectó los valores.
