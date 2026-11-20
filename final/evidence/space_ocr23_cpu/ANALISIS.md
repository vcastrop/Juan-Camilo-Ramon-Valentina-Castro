# Corrección de carga M1 para ZeroGPU — pendiente de prueba pública

El diagnóstico de startup20/11/2026 02:22:25UTC localiza la excepción en
adapters.py41 → PeftModel.from_pretrained → load_adapter → load_peft_weights →
safetensors.torch.load_file → interceptores ZeroGPU patching.py. Error RuntimeError,
sin mensaje privado retenido. Esto identifica la ruta, no todo el mensaje causal.

## Evidencia y corrección

PEFT0.17.1 usa infer_device si no recibe torch_device y pasa el dispositivo al
lector de safetensors. En ZeroGPU existe emulación CUDA durante startup. La
inferencia causal es que la selección automática del dispositivo conduce a esa
ruta interceptada. Nuestro M1 ya se ejecutaba en CPU; el .to(cpu) posterior no
evitaba una lectura previa en otro dispositivo.

Cambio acotado en una subclase exclusiva de despliegue: PeftModel.from_pretrained(base,path,torch_device='cpu'), seguido
del mismo .to(cpu).eval(). No cambia entrenamiento, modelo base/revisión,
tokenizador, pesos, etiquetas, longitud256, precisión ni lógica de predicción.
No se elimina M1 ni se sustituye por reglas o una cabeza aleatoria. `classify` se
hereda sin modificar y `integration_ocr23` conserva el sistema/lector20, alterando
solo el inicializador M1. El adaptador
incluye las cuatro matrices/bias de classifier y se conserva byte a byte.

Fuentes: [PEFT carga de adaptador](https://github.com/huggingface/peft/blob/v0.17.1/src/peft/peft_model.py),
[PEFT lector](https://github.com/huggingface/peft/blob/v0.17.1/src/peft/utils/save_and_load.py),
[HF emulación CUDA](https://huggingface.co/docs/hub/spaces-zerogpu).

## Paquete y verificación

- Commit inferencia final `5b42adc35d6e3225c93dfbda13ae2e1730bad1c8`.
- Payload SHA `3da4d933b4023a6b58186f2f08133145d2dfc5b5bed0ae82d2a259ce21191b80`.
- ZIP entregable aislado SHA `a0503f95d9567ac88ec05f2d7ab51b9b2eed032072ea47375ce9015e05c56b87`.
- Se agregan classifier_cpu23.py e integration_ocr23.py y cambia el manifiesto.
  Todos los miembros preexistentes, incluido adapters.py, pesos y corpus, son
  idénticos al22. No se regeneran respuestas.
- Los tres archivos README/requirements/packages son idénticos al22; subir
  **solo app.py y runtime_payload.zip juntos** del ZIP nuevo a la raíz.
- App conserva el diagnóstico seguro para cualquier fallo posterior. Manifest y
  todos los hashes/rutas verificados, 30 módulos y app compilados.
- Diez pruebas enfocadas pasaron con cargas simuladas: CPU explícita antes de
  leer el adaptador, base/revisión y checkpoint real conservados, privacidad,
  diagnóstico e interfaz/health. No hay inferencia neuronal local ni uso API.

La corrección aún NO demuestra arranque público, calidad M1 del nuevo entorno
ni consultas reales. Confirmar health con cuatro modelos/OCR/índice listos,
después smoke M1 y QA. Si vuelve a fallar, recibir el diagnóstico en lugar de
repetir cambios de versión. Evaluación21 y sus resultados históricos no se editan.

La primera implementación local modificaba adapters.py compartido; la suite
detectó siete errores de integridad histórica (364 tests, errors7), y no se
entregó ese paquete. Se restauró el archivo histórico exacto y se aisló la carga
CPU. Las dieciocho pruebas enfocadas, incluidas las guardas históricas18, pasaron
después. Esto no se oculta como si aquella suite hubiera aprobado.

Verificación final de la versión aislada: 364 pruebas final y128 M3, **492 en
total**, aprobadas. La comprobación de modelos continúa siendo simulada localmente;
la disponibilidad ZeroGPU y la inferencia M1 reales siguen pendientes.
