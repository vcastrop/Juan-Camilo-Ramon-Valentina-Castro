# Paquete OCR22 preparado; publicación aún pendiente

Código de inferencia y plantilla: `256945d2c373cc4b716f1e805097ae8e87a65f10`.
Payload SHA-256: `94e833cfc0c3a61b7ea1167a535dbe0f53ee0c531515b48238cdca8ca5d2b05d`.
ZIP exterior SHA-256: `326e3bf04893c1bb01b0b40121cd53644b54abddc77be7a78bbe05ff20725b20`.

Contiene cinco archivos de publicación: app.py, runtime_payload.zip,
requirements.txt, packages.txt, README.md. El ZIP exterior se descomprime;
runtime_payload.zip se sube tal cual. Tres imágenes de smoke se entregan en ZIP
separado y NO se suben como archivos de la app ni entran en el payload.

Se verificaron rutas/hashes del payload, 28 módulos compilables, manifiesto con
cuatro revisiones neuronales (sin VLM), licencia Qwen exacta y ausencia de
evaluaciones, gold, respuestas guardadas, juez y claves. Las clases VLM históricas
pueden existir en módulos compartidos; el entrypoint no las instancia.

Verificación: 359 pruebas final y128 M3 pasaron; después se ejecutaron seis
pruebas OCR específicas, incluida la nueva comprobación UI/health200/ready503.
El backend de estas pruebas es simulado: no se ha hecho inferencia neuronal
local ni consumido GPU/API. Carga/inferencia del perfil OCR sí existe en la
corrida20 de Colab, con cierre de calidad21, pero no prueba ZeroGPU.

Se conserva el candidato VLM sin modificarlo. ServiceOCR declara cuatro modelos,
OCR e índice por separado; no simula un quinto modelo. La salud indica versión
y hashes OCR reales y coincidencia con los idiomas de referencia. Un entorno
distinto exige revisar las consultas reales antes de declarar despliegue completo.

## Reproducción

Desde el commit fijado, obtener la licencia oficial de Qwen indicada en
`final.build_space_candidate.LICENSE_URL`, verificar `LICENSE_SHA` y ejecutar:

```powershell
python -m final.build_space_ocr --output space_ocr22_nuevo --license-file QWEN_RESEARCH_LICENSE.txt
```

El constructor exige que el código coincida con el commit, conserva fuentes,
adaptador y revisiones fijados, y no sube ni ejecuta modelos. Las instrucciones
de publicación/pruebas están en [DESPLIEGUE_OCR_22](../../DESPLIEGUE_OCR_22.md).

Pendientes: build y startup reales HF, siete rutas de smoke, eventos W&B y acceso
externo, reporte/roles/presentación y cierre de entrega. No se registra 100 %.
