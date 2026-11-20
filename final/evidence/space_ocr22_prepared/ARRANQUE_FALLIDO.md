# Primer arranque HF: construcción correcta, carga incompleta

Space commit3257875, startup20/11/2026 02:11:54UTC. Health confirma payload
256945d2c373cc4b716f1e805097ae8e87a65f10 pero readyfalse, modelos/lector vacíos
porque el backend no terminó de construirse. No implica que todo falló a la vez.

El log muestra carga de embeddings, colección Chroma, reranker y modelo base
RoBERTalex antes del mensaje genérico. La construcción instaló dependencias y
terminó correctamente. No hay excepción raíz impresa: la captura del app la
oculta. No afirmar que sea la clave, cuota, memoria, el adaptador o la GPU aún.

Avisos: Chroma/PostHog capture incompatible es telemetría secundaria; la cabeza
clasificadora se inicializa al cargar base y el adaptador incluye config y pesos
classifier que deben restaurarse posteriormente. El aviso no prueba pérdida de
entrenamiento ni carga correcta final. Los errores asyncio aparecen después del
mensaje de arranque fallido; no prueban causalidad.

## Diagnóstico mínimo

`final.startup_diagnostic_patch.py` adapta solo el handler de app.py generado:
registra tipo de excepción, código técnico reconocido y hasta diez frames de
archivo/función/línea sin rutas completas, mensajes, variables, URLs o claves.
No cambia payload, modelos, adaptador, evaluación ni secretos. No usa API pagada.
La versión de inferencia sigue256945d; diagnostic_version identifica este parche.

Nueve pruebas de diagnóstico/interfaz/salud OCR pasaron con backend simulado.
No equivale a reparar la causa raíz; se necesita observar el siguiente arranque.

Subir únicamente app.py del ZIP de diagnóstico a la raíz del Space, conservar
los otros cuatro archivos y secretos. Esperar y enviar la línea JSON
`contractrisk_startup_diagnostic` y las líneas que la rodean. No cambiar versiones
ni eliminar M1 para fingir disponibilidad. Los smoke y W&B siguen pendientes.
