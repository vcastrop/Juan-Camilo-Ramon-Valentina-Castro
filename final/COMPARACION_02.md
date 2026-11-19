# Comparación 02 — corregir interfaz sin cambiar la evaluación

Estado 18/11/2026: preparado, con regresiones locales aprobadas; **inferencia real T4 pendiente**. [Notebook nuevo](ContractRisk_Final_Comparacion_02_Colab.ipynb). Main, Space y presupuesto del juez permanecen intactos.

## Qué falló

[Comparación 01 auditada](evidence/comparison_01/ANALISIS.md): el adaptador nuevo trató las funciones devueltas por `sistemas_m3.construir` como objetos con `.predict`. Se reprodujo exactamente `'function' object has no attribute 'predict'`. El error era del adaptador, no del usuario, la clave de W&B, Gemini ni una calificación. Las pruebas anteriores representaban mal la interfaz; se reemplazaron por la fábrica y wrappers reales de M3, con dobles solo de ML/recuperación.

La T4, SQLite, índice, reranker, carga del generador FP16 y prueba pequeña NF4 funcionaron. La prueba pequeña no demuestra carga del generador NF4 completo. Hubo cero respuestas evaluadas, por lo que reiniciar con la interfaz corregida no selecciona mejores respuestas.

## Cambios limitados

- Adaptador de función `pregunta -> registro` a método `.predict(question)`, para ambos perfiles textuales.
- Versión de colección `common-collection-1.0.1-callable-fix`. No cambian preguntas/referencias, prompts, modelos/revisiones, semilla, límite de tokens, recuperación, VLM, cuantización, orden o reglas de dominio/eficiencia.
- Verificación del ZIP de 01, cero predicciones y configuración previa antes de cargar modelos. Cualquier cambio de configuración distinto de la versión bloquea esta recuperación.
- Errores futuros incluyen ubicaciones de código sanitizadas, sin mensajes, líneas de código ni variables. Esto facilita diagnóstico sin exponer entradas o credenciales.

Mantiene los cinco perfiles y 22 casos de [Comparación 01](COMPARACION_01.md), sus límites de representatividad y medición. QA sin RAG sigue siendo una adaptación, no la clasificación M2. M1 no se carga en este benchmark; su prueba pública sigue pendiente. Calidad semántica, juez y aceptación de eficiencia no se inventan: siguen pendientes.

## Ejecución

1. Abrir **Comparación 02**, no repetir el notebook 01 antiguo.
2. Usar una sesión nueva GPU T4 y habilitar el secreto existente `WANDB_API_KEY` para este notebook. No necesita Gemini, nueva clave, permisos de pago ni modificar Drive.
3. Ejecutar las celdas en orden. Se recogerán 110 filas si completan cinco perfiles; calentamientos guardados y excluidos. Las mediciones reales se auditarán, no se anticipa una mejora de la cuantización.
4. Si termina o falla, descargar `contractrisk_final_comparacion02_resultados.zip` y el notebook con salidas. Si falla la inferencia, ejecutar las celdas finales de inspección/descarga; no repetir para buscar resultados favorables.
5. Enviar ambos archivos. No guardar sobre main desde Colab. La versión anterior permanece archivada como evidencia del fallo.
