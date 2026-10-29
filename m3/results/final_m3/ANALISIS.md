# Auditoría de la corrida final M3 sobre el gold

Fecha: 29/10/2026. Revisión técnica asistida por Claude Code; no sustituye la revisión humana del equipo. Originales sin modificar en esta carpeta (ZIP de Colab descomprimido y notebook ejecutado).

## Integridad

- Colab Tesla T4, inicio 2026-10-29T18:06:35Z, `status: completed`, código `6026ac4` (`commit.txt`). Los 28 hashes de `metadata.json` coinciden (corregido tras la revisión; decía 23 por error) con los archivos del repositorio; hashes de corpus y gold verificados por el script antes de correr.
- `tests.log`: 79 pruebas aprobadas. Índice reconstruido desde cero: 24 fichas, 133 chunks, 16,6 s.
- 72 respuestas (6 variantes × 12), 72 juicios válidos al primer o segundo intento, 36 casos RAGAS con 300 llamadas al juez y 0 respuestas sí/no sin parsear.
- `report_m3.py` ejecutado localmente sobre `harness_rows.jsonl` y `ragas.jsonl` reproduce `tablas_m3.md` byte a byte.
- Ninguna respuesta fue sustituida, repetida ni seleccionada. Los avisos de telemetría de Chroma en `execution.log` son inocuos.

## Hallazgos que el harness automático no capta

1. m3_009 (avanzado y final): la explicación dice «lo que sugiere una posible irregularidad», contra el criterio del gold. La regla de acusación solo detecta afirmaciones fuertes, así que es un **falso pase de dominio**. La respuesta «No» es además ambigua frente a una pregunta de dos partes.
2. m3_012 (avanzado y final): conclusión de auditoría **inventada** a partir de «Duración registrada». El juez le dio 4: es el mismo fallo de juez ya observado en la calibración v5.
3. m3_011 (avanzado y final): el texto niega tener la cláusula, pero `abstencion=false`. El harness lo marca correctamente como `no_se_abstiene`.
4. m3_007 (final): la cifra es correcta gracias a la herramienta, pero la explicación es errónea («sumando las diferencias») y omite los operandos.
5. RAGAS: el juez 3B rechaza chunks que contienen literalmente el dato (context precision 0 con recall 1 en m3_001 y m3_010) y fechas presentes en la ficha (m3_009). El divisor de afirmaciones parte `CO1.PCCNTR.<n>` en el punto (defecto de `ragas_m3.split_statements`), lo que añade fragmentos como «1109703::c003» a faithfulness. No se corrigió después de la corrida.
6. Agente: 9/10 preguntas no aritméticas sin llamada; m3_009 hizo 2 llamadas inválidas rechazadas más una bloqueada por duplicada (+6,8 s). Las dos preguntas de cálculo llamaron la herramienta con los IDs correctos al primer paso.
7. Ablación denso+rerank, m3_008: salida inválida («Unknown citation» en ambos intentos, 444 y 426 tokens) y 43,5 s.

## Detalle de las filas con RAGAS

| Variante | Caso | Exactitud | Juez | Dominio | Respuesta |
|---|---|---:|---:|---|---|
| rag_ingenuo | m3_001 | 0.00 | 3 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contratan obras con modalidad de contratación mínima cuantía y se contrata con la entid |
| rag_ingenuo | m3_002 | 0.00 | 4 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contrata una obra y la entidad que lo contrata es la CGR- GERENCIA DEPARTAMENTAL QUINDI |
| rag_ingenuo | m3_003 | 0.00 | 2 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contratan obras con modalidad de contratación mínima cuantía y se contrata con la entid |
| rag_ingenuo | m3_004 | 0.00 | 3 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contratan obras con modalidad de contratación mínima cuantía y se contrata con la entid |
| rag_ingenuo | m3_005 | 0.00 | 4 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contrata una obra y la entidad que lo contrata es la CGR- GERENCIA DEPARTAMENTAL QUINDI |
| rag_ingenuo | m3_006 | 0.00 | 2 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | Se contratan obras con modalidad de contratación mínima cuantía y se contrata con la entid |
| rag_ingenuo | m3_007 | 0.00 | 2 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | 5687267 |
| rag_ingenuo | m3_008 | 0.00 | 2 | no: hechos_incompletos, falta_cita_requerida, cita_ficha_ajena | 1076363 - 36025130 = -34948767 |
| rag_ingenuo | m3_009 | 1.00 | 4 | sí | No |
| rag_ingenuo | m3_010 | 1.00 | 4 | sí | Mínima cuantía |
| rag_ingenuo | m3_011 | 0.00 | 2 | no: no_se_abstiene | registrada: 6 Mes(es) |
| rag_ingenuo | m3_012 | 1.00 | 4 | sí | La auditoría de ejecución física no se menciona para el contrato CO1.PCCNTR.1083652. |
| rag_avanzado | m3_001 | 1.00 | 5 | sí | Se contrata la construcción del cerramiento del aeropuerto Golfo de Morrosquillo de Tolú y |
| rag_avanzado | m3_002 | 1.00 | 4 | sí | Se contrata la adquisición de elementos de protección personal para los servidores de la R |
| rag_avanzado | m3_003 | 0.50 | 5 | no: hechos_incompletos | Se contrata la adquisición de equipo de investigación con destino a la Escuela de Infanter |
| rag_avanzado | m3_004 | 0.50 | 4 | no: hechos_incompletos | Se contrata una consultoría y la entidad que lo contrata es el Instituto de Financiación,  |
| rag_avanzado | m3_005 | 0.50 | 4 | no: hechos_incompletos | Se contrata un arrendamiento de inmuebles ubicados en la calle 13 # 11-25 de la ciudad de  |
| rag_avanzado | m3_006 | 0.50 | 4 | no: hechos_incompletos | Se contrata la prestación de servicios para los aeropuertos San Bernardo de Mompoqu y Las  |
| rag_avanzado | m3_007 | 0.00 | 2 | no: hechos_incompletos, falta_cita_requerida | 5147 |
| rag_avanzado | m3_008 | 0.00 | 4 | no: hechos_incompletos | 19000671 H1 - 19001143A H1 |
| rag_avanzado | m3_009 | 1.00 | 4 | sí | No |
| rag_avanzado | m3_010 | 1.00 | 4 | sí | Mínima cuantía |
| rag_avanzado | m3_011 | 0.00 | 4 | no: no_se_abstiene | No se encontró la cláusula de multas en el contrato CO1.PCCNTR.1088236. |
| rag_avanzado | m3_012 | 0.00 | 4 | no: no_se_abstiene | La auditoría de ejecución física concluyó que el contrato CO1.PCCNTR.1083652 tiene una dur |
| sistema_final | m3_001 | 1.00 | 5 | sí | Se contrata la construcción del cerramiento del aeropuerto Golfo de Morrosquillo de Tolú y |
| sistema_final | m3_002 | 1.00 | 4 | sí | Se contrata la adquisición de elementos de protección personal para los servidores de la R |
| sistema_final | m3_003 | 0.50 | 5 | no: hechos_incompletos | Se contrata la adquisición de equipo de investigación con destino a la Escuela de Infanter |
| sistema_final | m3_004 | 0.50 | 4 | no: hechos_incompletos | Se contrata una consultoría y la entidad que lo contrata es el Instituto de Financiación,  |
| sistema_final | m3_005 | 0.50 | 4 | no: hechos_incompletos | Se contrata un arrendamiento de inmuebles ubicados en la calle 13 # 11-25 de la ciudad de  |
| sistema_final | m3_006 | 0.50 | 4 | no: hechos_incompletos | Se contrata la prestación de servicios para los aeropuertos San Bernardo de Mompoqu y Las  |
| sistema_final | m3_007 | 0.33 | 4 | no: hechos_incompletos | 168000000 COP |
| sistema_final | m3_008 | 1.00 | 4 | sí | 15387424 COP |
| sistema_final | m3_009 | 1.00 | 4 | sí | No |
| sistema_final | m3_010 | 1.00 | 4 | sí | Mínima cuantía |
| sistema_final | m3_011 | 0.00 | 4 | no: no_se_abstiene | No se encontró la cláusula de multas en el contrato CO1.PCCNTR.1088236. |
| sistema_final | m3_012 | 0.00 | 4 | no: no_se_abstiene | La auditoría de ejecución física concluyó que el contrato CO1.PCCNTR.1083652 tiene una dur |

## Revisión posterior del equipo y del profesor (29/10/2026)

Se confirmaron, y se corrigen sin modificar ningún archivo original de esta corrida, los siguientes puntos:
- Defectos deterministas de `m3-harness-1.0`: una cifra aceptada dentro de otra mayor, una mención negada contada como presencia y una acusación atenuada sin detectar. Se recalificó con `m3-harness-1.1` en `../final_m3_rescore_v1_1/`. Solo cambia el dominio de m3_009 (avanzado y final).
- La «ficha gold entregada 10/10» no implica recuperación del dato. En m3_007 y m3_008 el avanzado no trae los campos de valor, y en m3_004 y m3_006 falta parte de la descripción.
- RAGAS 1.0 tiene segmentación defectuosa, y su precision/recall es una adaptación, no la variante del laboratorio; con el juez 3B sus diferencias entre filas no son concluyentes. Se preparó RAGAS 1.1 (`../../rerun_ragas_m3.py`), pendiente de ejecutar en GPU.
