---
title: ContractRisk Colombia
emoji: 📋
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.16.0
python_version: 3.12
app_file: app.py
pinned: false
---

# ContractRisk Colombia — OCR, fuentes y herramientas

**Built with Qwen. Solo investigación/evaluación no comercial.** Prototipo
académico sobre 24 fichas contractuales públicas. No determina fraude,
autenticidad, cumplimiento físico ni aptitud jurídica. La decisión es humana.

Pregunta en texto o carga una captura de ficha con identificador, modalidad,
objeto y valor rotulados. Selecciona el modo M1 para suficiencia descriptiva,
no para clasificar fraude. Acepta el aviso y pulsa Consultar. Verifica siempre
respuesta, explicación y fuentes. No subas documentos privados ni datos personales.

## Componentes y evidencia

Cuatro modelos neuronales: generador Qwen2.5-3B FP16, embeddings multilingües,
reranker y RoBERTalex con adaptador M1. Lectura de imagen: Tesseract CPU, dos
segmentaciones del mismo motor, no dos lectores independientes ni un VLM.
No se carga Qwen2-VL. Recuperación híbrida con fuentes completas, herramienta
numérica y controles de abstención/consistencia. Referencia en Colab T4:
dominio18/22 y juez4,4545/5; cuatro fallos textuales conocidos. Conjunto pequeño
ya inspeccionado, no validación ciega ni certificación de uso real.

En la imagen adversarial el OCR descartó la instrucción antes del generador:
no demuestra inmunidad del generador. Los campos acotados omiten encabezado y
entidad; no es OCR universal. Coincidir con el snapshot no autentica la imagen.
NF4 no se despliega porque perdió calidad en la comparación histórica.

## Arranque y observabilidad

Subir juntos cinco archivos en la raíz: app.py, runtime_payload.zip,
requirements.txt, packages.txt y README.md. Hardware ZeroGPU. El arranque carga
los modelos; las consultas usan asignación GPU bajo demanda. Un estado Running
no prueba disponibilidad: el botón de salud y /readyz deben indicar listo.
La salud muestra cuatro modelos, OCR con versión/hashes, índice y commit real.
Si los datos de idioma difieren de la evaluación, se indica expresamente; hay
que revisar la lectura real en el nuevo entorno antes de considerar el despliegue
comprobado. La versión procede del manifiesto, no de CONTRACTRISK_VERSION.

Secreto WANDB_API_KEY existente; variables WANDB_ENTITY=jcramonp-eanit,
WANDB_PROJECT=contractrisk-final y WANDB_BASE_URL=https://api.forge.coreweave.com.
No necesita GEMINI_API_KEY ni API pagada. Sin W&B la inferencia sigue disponible,
pero observabilidad queda deshabilitada. queued_check_dashboard solo significa
encolado: verificar run, eventos y acceso externo por separado.

Solo metadatos técnicos en logs/W&B, no pregunta, descripción, imagen ni OCR.
Las fuentes aparecen en la interfaz, no se envían como contenido a W&B. Imágenes
pueden quedar temporalmente en caché del framework: limpieza periódica cada hora
para archivos antiguos, no borrado inmediato garantizado. Límite 10 MB/12 MP,
cola cuatro y concurrencia uno. Cuota/disponibilidad dependen del proveedor.

## Reproducción y licencias

[Código, evidencia y guía](https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro/tree/Entrega/contractrisk-final/final).
Revisiones fijadas en manifest.json del payload; sin gold, respuestas guardadas,
juez ni claves. Qwen2.5-3B usa Qwen Research License, no Apache2. Copia exacta
de su licencia y NOTICE dentro del payload. No se redistribuyen pesos base;
el adaptador M1 conserva su procedencia. Código no cambia licencias de modelos.
[Licencia Qwen fijada](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/aa8e72537993ba99e69dfaafa59ed015b17504d1/LICENSE).
