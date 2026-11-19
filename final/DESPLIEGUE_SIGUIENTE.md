# Próximo hito: servicio contractual público

La evaluación de los cinco perfiles está cerrada en
[scorecard completo](evidence/domain_review46/scorecard_complete.csv).
No repetir entrenamientos, calibración o evaluación 14 para publicar la interfaz.
El candidato es FP16: NF4 se rechaza según los umbrales acordados. Esto no
certifica seguridad de FP16 ni elimina sus seis fallos medidos.

## Reutilizar, no sustituir por respuestas simuladas

- QA: `collection_profiles.build_profile('integrated_fp16', ...)`, que reutiliza
  el generador nativo, recuperación, fuentes completas, herramienta y Vision evaluados.
- M1: `adapters.Classifier`, adaptador LoRA histórico sobre RoBERTalex, en CPU,
  accesible mediante `IntegratedSystem.predict(..., mode='sufficiency')`.
- Visión: el lector real y controles de campo ausente/contradicción ya evaluados.
- No cargar referencias, respuestas esperadas, scorecards o notas del juez en la
  inferencia pública. Ninguna clave Gemini es necesaria para responder consultas.

## Antes de sustituir los cuatro archivos públicos

1. Preparar un candidato separado del Space de infraestructura. Fijar revisión
   del código, modelos, corpus y adaptador; comprobar licencias y procedencia.
2. Revisar inicialización compatible con ZeroGPU: importar `spaces` antes de CUDA,
   colocar modelos en `cuda` durante inicio bajo la emulación del SDK y ejecutar
   inferencia dentro de `@spaces.GPU`. La documentación actual desaconseja carga
   diferida o traslado de modelos a CUDA dentro del callback. No suponer que un
   script de Colab funciona igual. Verificar compatibilidad real de loader/torch/SDK.
   [Documentación oficial consultada](https://huggingface.co/docs/hub/spaces-zerogpu).
3. Asegurar SQLite/FTS5 para Chroma antes de importarlo; evitar repetir el fallo
   de Colab. No cambiar silenciosamente recuperación o decodificación.
4. Inicializar índice y componentes reales, con límites de pregunta/descripción,
   tamaño/píxeles de imagen, concurrencia y cola. Mensajes de error sanitizados.
5. Preparar health sin GPU/pregunta real y readiness que no diga listo por tener
   solo el proceso vivo. No exponer secretos o rutas locales en esos endpoints.
6. Conectar telemetría real: hora, latencia, RAG, visión, clasificador, herramienta
   exitosa y abstención. Usar `tool_usage` para distinguir router de ejecución;
   no repetir el contador histórico `bool(tool_trace)`/`bool(tool_calls)`.
7. No guardar preguntas, imágenes, OCR, identificadores ni respuestas en JSON/W&B.
   Auditar caché temporal de archivos del framework y describir retención real
   antes de recibir documentos del público; no prometer ausencia total de caché.
8. Probar candidato con mocks locales y después con modelos reales en el entorno
   objetivo. Solo entonces actualizar el Space; main no se fusiona automáticamente.

## Evidencia pública obligatoria

- Texto con fuentes, consulta numérica con traza, captura legible, falta de dato,
  imagen blanca/instrucción adversarial y error de entrada. No escoger solo casos fáciles.
- Modo M1 visible con advertencia: suficiencia descriptiva, no dictamen de fraude.
- Health y readiness comprobados desde la URL, incluyendo arranque frío.
- JSON de peticiones sin datos personales y eventos reales en W&B, no solo Colab.
- Enlace accesible al evaluador o capturas sin información sensible. El estado
  `finished` de una run no prueba por sí solo acceso público.
- Documentar diferencias entre la T4 del experimento y ZeroGPU del despliegue;
  no comparar sus latencias como antes/después de cuantización.

No están verificados estos hitos por cerrar la revisión de dominio. La última
versión pública comprobada es de infraestructura y no constituye la entrega final.
Mientras se prepara el candidato, faltan también portada/README, diagrama,
responsabilidades reales del equipo, sección de IA y diapositivas/demo de diez
minutos, reproducción limpia y cierre de entrega con PR/merge autorizado.
