# Primera integración real — desarrollo, no evaluación final

Ejecutar `ContractRisk_Final_Integracion_01_Colab.ipynb` en **una sesión nueva con T4**. El notebook clona `Entrega/contractrisk-final`, registra el commit, instala versiones y ejecuta pruebas antes de inferencia. El Space actual no se reemplaza con este candidato.

## Qué conecta

- Adaptador M1 real: señal de suficiencia descriptiva, confianza no calibrada, ejecución CPU.
- RAG M3 real: embeddings, Chroma, híbrido/RRF y reranking; generador y herramienta heredados. Capa nueva agrega fichas completas pequeñas a las fuentes seleccionadas, para evitar que truncar un chunk elimine campos. Es una modificación identificada, no los resultados M3 originales.
- Controles nuevos de tipo de fuente ausente, contrato desconocido, formato y discrepancia de ID pregunta/imagen. No son una garantía de detectar toda alucinación.
- VLM Qwen2-VL-2B real: campos nulos permitidos, transcripción y JSON validado, sin ejecución de instrucciones de la imagen.
- W&B opcional: métricas técnicas sin preguntas, imágenes ni transcripciones; `finish()` en bloque finally.

## Datos de prueba

Preguntas de desarrollo, dos descripciones sintéticas sin etiquetas humanas adjudicadas y cuatro imágenes: dos representaciones rasterizadas de campos públicos del snapshot, un cambio de contraste y una imagen vacía. **No son capturas reales ni un nuevo gold humano.** No se carga `m3/eval/gold_v1/eval_set.json` ni se produce una nota académica.

El conjunto final requerirá al menos cinco casos visuales revisados por humanos y más adversariales; estas cuatro imágenes no sustituyen ese pendiente.

## Memoria y latencia

Para reducir riesgo de OOM en T4 se cargan generador y VLM de manera secuencial: texto, lectura visual, descarga del VLM y generación desde lecturas visuales guardadas. La última fase prueba la conexión real entre componentes, pero **reutiliza las extracciones**. No mide latencia multimodal fresca de punta a punta ni demuestra carga simultánea en producción.

Las latencias del VLM y de la orquestación se guardan por separado. No sumarlas como si fueran un benchmark controlado del sistema final. El perfilado de producción y la técnica de eficiencia vendrán después.

## Revisión del equipo

Comprobar las etiquetas M1 como señales, no veredictos de fraude. Comparar cada campo leído con la imagen. Revisar las respuestas finales y sus citas, no aprobar solo porque el JSON es válido. Inspeccionar el cálculo con ambos operandos y confirmar abstención en imagen vacía y fuentes ausentes.

Devolver el ZIP completo y el notebook con sus salidas. El ZIP preserva metadata, filas, fixtures y fallos. No editar respuestas; no repetir buscando mejores cifras. `quality_approved` permanece false hasta revisión explícita del equipo.

Si falla un caso, se guarda su error y se continúa cuando es posible. Si falla una carga de modelo o etapa global, metadata y traceback se conservan. No publicar imágenes o preguntas privadas en este paquete.

## Configuración W&B

En secretos de Colab: `WANDB_API_KEY`, habilitado para el notebook. La primera celda solo pasa su valor al proceso de ejecución, sin imprimirlo. Si no existe, la integración continúa localmente y lo declara. Acceso externo al proyecto debe verificarse aparte; las capturas anteriores son de infraestructura, no de consultas finales.
