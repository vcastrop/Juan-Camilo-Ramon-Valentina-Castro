# Segundo intento: construcción superada, arranque fallido

Fuente: log y captura proporcionados por el usuario el 16/11/2026, commit HF `236870d`. La instalación de dependencias terminó y la imagen se publicó. El contenedor reportó puerto 7860 ocupado y `No @spaces.GPU function detected during startup`.

Corrección del adaptador de despliegue, sin cambios de modelos ni métricas:

- `import spaces` antes de bibliotecas que puedan inicializar CUDA.
- Callback decorado `gpu_operation` conectado directamente al botón Gradio; registro W&B en callback CPU posterior a éxito.
- Un único inicio nativo `demo.launch()`, sin `uvicorn.run()` independiente ni `mount_gradio_app`.
- Endpoints de salud incorporados como rutas adicionales del servidor Gradio. No se cambia arbitrariamente el puerto público del Space.

Verificación local: inicio real de Gradio en puerto libre, HTTP `/` 200, `/healthz` 200 y `/readyz` 503; cierre limpio del servidor. El callback registrado lleva el marcador GPU simulado en esta prueba CPU. Configuración SDK W&B válida, clave no recibida. Se añade prueba estructural para impedir volver al callback GPU oculto o inicio Uvicorn independiente.

No se afirma haber reproducido el entorno de ZeroGPU localmente. Reconstrucción y ejecución GPU reales siguen pendientes del siguiente intento del titular. La causa del fallo de detección se corresponde con el patrón de callback indirecto documentado; no se da por probada la resolución remota del conflicto de puerto hasta observar el Space.
