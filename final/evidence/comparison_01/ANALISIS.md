# Comparación 01: error del adaptador antes de evaluar casos

Auditoría del 18/11/2026, con ejecución 19/11 02:05–02:08 UTC (18/11 21:05–21:08 Bogotá). [Hashes y comprobaciones](audit.json). ZIP/notebook originales conservados sin editar. Código `882985171cc4a70d37857f59f78483a7bb76a012`; 87 hashes de fuentes verificados contra Git. Cinco celdas ejecutadas, una salida RuntimeError esperada por la detención del subprocess.

## Causa reproducida

`sistemas_m3.construir` devuelve un diccionario de **funciones** `pregunta -> registro`. El adaptador nuevo de comparación intentó `historical['sin_rag'].predict(...)` y pasó otra función como si fuera un objeto con `.predict` para el perfil M3. Esto produce `'function' object has no attribute 'predict'`.

El error pertenece al código nuevo de comparación. No es fallo del usuario, de sus claves, de Gemini ni una mala respuesta contractual. Las pruebas anteriores pasaban porque sustituían la fábrica por dobles con `.predict`, que no representaban el contrato real de M3. Se reemplaza esa prueba por la fábrica/wrappers reales y dobles solo para los modelos y recuperación costosos.

Se detuvo en `qa_no_rag_fp16:warmup`, antes de llegar a los 22 casos. **Cero perfiles completos y cero filas de evaluación guardadas.** No hay respuestas válidas que seleccionar o reemplazar al reiniciar la colección corregida.

## Lo que sí funcionó y lo que no demuestra

- Tesla T4, Python 3.13.16, torch 2.14.1+cu130; SQLite con FTS5 comprobado.
- Carga del generador 3B FP16 completada, índice/reranker preparados y prueba pequeña del kernel NF4 aprobada. Esa prueba pequeña no equivale a cargar ni evaluar el generador completo NF4.
- W&B conectó y cerró según logs; el acceso externo al dashboard no se comprobó aquí.
- Logs: 206 pruebas final y 128 M3 aprobadas. No cubrían correctamente la interfaz de la fábrica; no equivalen a éxito de inferencia.
- Mensajes de telemetría opcional de Chroma y advertencias de API de torch aparecen antes del fallo, pero el programa continuó hasta el calentamiento. No son la causa reproducida de esta detención. No se cambian dependencias para ocultar avisos.
- Sin evaluación de calidad, ahorro de memoria, latencia comparativa ni aceptación de cuantización. API del juez y registro de presupuesto no se usan.

## Corrección

El adaptador ahora llama directamente a la función de M3 y ofrece `.predict` al ejecutor común, sin cambiar M3 histórico, preguntas, referencias, prompts, modelos, precisión, semillas, límites de generación o reglas. Se verifica el ZIP original y que no había predicciones antes de admitir el reinicio. Si se cambian ajustes de inferencia, la recuperación se bloquea.

Se añaden ubicaciones sanitizadas de código a errores futuros (archivo/línea/función, sin mensaje, texto fuente ni variables). [Comparación 02](../../COMPARACION_02.md) preparada; todavía requiere ejecución real en T4. Main y Space no se modifican.
