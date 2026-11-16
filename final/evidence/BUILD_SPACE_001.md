# Primer intento de construcción del Space

Fuente: log proporcionado por el usuario; inicio 16/11/2026 07:54:57, commit HF `c6a41e9`.

El builder ZeroGPU ejecutó una instalación que incluía `spaces==0.51.3`, mientras que nuestro requirements.txt exigía `spaces==0.52.0`. Pip rechazó las dos versiones exactas con `ResolutionImpossible`; la aplicación no llegó a ejecutarse. No fue un error de W&B, de GPU, de secretos ni de inferencia.

Corrección: alinear únicamente el pin de spaces con `0.51.3`, observado en ese builder. Se añade una prueba de regresión para el contrato observado; no garantiza que futuras imágenes de Hugging Face no cambien. Si el builder cambia su pin, revisar el nuevo log y volver a validar.

La prueba HTTP local anterior simuló el decorador GPU y no instaló spaces/torch. Por ello no detectó este conflicto. No presentar aquella prueba como verificación del entorno Linux completo.

Siguiente comprobación pendiente: reconstrucción real con requirements corregido, arranque, health check, asignación GPU y sincronización W&B. Corregir este conflicto no demuestra por sí mismo que esas etapas hayan pasado.
