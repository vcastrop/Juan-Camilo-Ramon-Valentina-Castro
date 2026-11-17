# Control de consistencia entre imagen y snapshot — integración 0.3

Implementado después de revisar visual 03. No es corrección del OCR ni validación ciega; es mitigación de propagación de contradicciones. Ningún prompt/peso del modelo ni referencia aprobada se cambió. [Fallo original](evidence/visual_03/ANALISIS.md).

## Regla

En modo QA con imagen legible, después del control de ID/campos ausentes y antes del generador:

1. Buscar por ID leído en el snapshot fuente normal del sistema; no se consultan respuestas gold.
2. Comparar monto y modalidad presentes en ambas fuentes solo cuando el campo del snapshot tiene un único literal inequívoco.
3. Montos: igualdad decimal exacta, sin floats, prefijos ni conjeturas de separadores. Modalidad: normalización de mayúsculas, espacios y tildes; no paráfrasis semánticas.
4. Si difieren, devolver `abstencion=true`, guard `visual_source_conflict`, ambos literales identificados y citas de imagen y ficha. No ejecutar generador/router/herramienta para confirmar uno.
5. Si no difieren, continuar por la ruta normal. Registrar qué campos se compararon. No modificar la lectura visual ni el snapshot.

Ejemplo: «lectura visual 2500000000; snapshot 250000000; no se confirma cuál es correcto; revise imagen y versión de ficha». El snapshot podría ser antiguo y la imagen podría ser de otra versión: el control no afirma automáticamente que la imagen esté equivocada ni que el documento sea auténtico.

## Alcance y límites

- Ausencia de monto leído sigue causando abstención si la pregunta lo pide, aunque el corpus sí lo contenga.
- ID desconocido/sin ID, campo fuente ausente/duplicado o formato no canónico: comparación no disponible o parcial. No confundir con acuerdo. Los datos ambiguos no se eligen ni reparan automáticamente.
- No compara semántica del objeto, autenticidad, fechas ni todos los posibles tipos de dato. No detecta errores compartidos por las dos fuentes o un ID leído incorrectamente que coincida con otro registro.
- Si los campos coinciden, aún puede fallar la respuesta/explicación del generador. Esta regla no sustituye validación de respuesta, juez calibrado, adversariales o revisión humana.
- El bloqueo puede rechazar una imagen correctamente leída que difiera de un snapshot desactualizado. Es una abstención conservadora que el usuario debe resolver, no un resultado positivo de exactitud.
- Las consultas solo textuales y el modo de suficiencia M1 mantienen su comportamiento; este control se aplica únicamente a QA visual.

## Evidencia CPU

`python -m final.replay_source_guard --output <directorio_nuevo>` reproduce las diez lecturas de visual 03. [Metadata](evidence/source_guard_cpu_01/metadata.json) y [filas](evidence/source_guard_cpu_01/replay_rows.jsonl).

Resultado: solo vis_04 cambia a abstención por conflicto; las otras nueve salidas se conservan. Los adaptadores del replay usan lecturas y respuestas guardadas: **cero llamadas nuevas a modelos**. No medir sus latencias como rapidez de inferencia ni recalificarlo como mejora visual independiente. El caso legible vis_04 sigue sin obtener su respuesta gold; la mitigación evita afirmar el monto incorrecto.

53 pruebas final CPU y 128 M3 pasan: incluyen fallo real guardado, montos con cero adicional, igualdad decimal, modalidad distinta, fuentes ambiguas, ausencia de campos, ID desconocido y ausencia de mutación. Estas pruebas no reemplazan comprobación del servicio público.

## Ruta siguiente

No repetir visual 03 solo para elevar su cifra. Conservar el fallo y esta reproducción como evidencia de desarrollo. La siguiente corrida de modelos debe pertenecer al protocolo común final, con integración 0.3 identificada, calibración del juez y criterios previos de calidad/eficiencia. La comparación antes/después mantendrá el mismo control de consistencia en ambos lados para no atribuir su efecto a cuantización.
