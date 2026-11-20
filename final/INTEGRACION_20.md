# Integración OCR 20 — nuevo perfil, evaluación común conservada

Estado: preparado; sin inferencia real de esta versión todavía. [OCR 19](evidence/ocr19_completed/ANALISIS.md)
aportó extracción útil en su muestra, no respuestas contractuales validadas.

## Qué cambia y qué no

- Perfil nuevo `integrated_ocr20_fp16`; el código Qwen/VLM histórico y sus resultados
  permanecen intactos. No se hereda su 16/22 ni se reescribe la tabla FP16/NF4.
- OCR Tesseract19 sustituye al VLM como lector de esta versión. **No se carga
  Qwen2-VL**. Siguen el generador FP16, embeddings, reranking y clasificador M1
  con las revisiones fijadas. La política visual cambió: no decir que solo cambió UI.
- Solo campos etiquetados y aceptados por OCR se presentan como evidencia visual;
  texto OCR libre, encabezados e instrucciones sin etiqueta quedan en auditoría
  local, no en el contexto del generador. Los campos siguen siendo datos no
  confiables, no instrucciones. Esto no prueba inmunidad ante toda inyección.
- Siguen bloqueos por valor/modalidad en contradicción, campos solicitados ausentes,
  imagen vacía, lectura ambigua e ID de pregunta distinto. Se añade rechazo de
  ficha visual fuera del snapshot en QA para no citar otro contrato.
- M1 recibe descripción textual o el objeto aceptado de la imagen, sin dictaminar
  fraude. Su confianza no calibrada y sus errores históricos no desaparecen.
- Una extracción OCR por petición, dos segmentaciones fijas, sin reparar cifras
  desde el corpus ni reintentar por mala respuesta. El corpus se compara después.

## Qué se ejecutará

**22 casos comunes originales**, mismos PNG, preguntas, referencias y harness.
Se conservan también errores y abstenciones. Las referencias no entran al sistema;
se usan tras inferencia en diagnósticos automáticos, no como notas semánticas.

**16 comprobaciones aparte:** doce imágenes de OCR19, mismatch de ID,
pregunta adversarial de auditoría inexistente, M1 por texto y M1 por imagen.
Las fichas ficticias fuera del snapshot deben rechazarse en QA aunque el OCR
las lea bien. El monto alterado debe disparar contradicción; no basta leerlo.
Estas 16 no amplían el eval set común ni se suman a sus denominadores.

El recolector se detiene ante fallo técnico y conserva parciales. No usa juez,
claves ni W&B. Después faltará revisar/juzgar las nuevas respuestas con el mismo
harness antes de completar la fila nueva de calidad; notas ausentes no son cero
ni aprobación. El presupuesto API anterior no se toca.

## Ejecutar

1. Abrir `ContractRisk_Final_Integracion_20_Colab.ipynb`.
2. Usar **GPU T4**, necesaria para el generador, aunque OCR sea CPU.
3. Ejecutar en orden. Si falla, descargar el parcial con la última celda.
4. Enviar ZIP y notebook con salidas. No repetir 17, 18 o 19; no subir al Space aún.

La prueba recoge una pasada en T4 y registra entorno/procedencia, pero no es un
nuevo experimento de eficiencia ni prueba el ciclo de vida ZeroGPU. El despliegue
deberá incorporar Tesseract/idiomas y salud real de sus cuatro modelos neurales
y motor OCR; no fingir que sigue cargado el VLM para conservar cinco banderas.
La interfaz pública anterior es todavía de infraestructura y no se reemplaza aquí.

Comprobación local: suite final 338 y M3 128 aprobadas; se comprobó después una
prueba adicional del recolector completo con dobles (38 llamadas, solo entradas
permitidas, calidad pendiente). Las nueve pruebas específicas de integración
pasan. Estos resultados no contienen ejecuciones reales T4 de la versión20.
