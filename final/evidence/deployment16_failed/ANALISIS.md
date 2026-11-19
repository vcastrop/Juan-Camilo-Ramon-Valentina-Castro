# Prueba de despliegue 16 — fallo de instalación, no resultado del sistema

Recepción 19/11/2026. ZIP original conservado sin modificar:
`original_results.zip`, SHA256
`cfb2344cf6cd7550f8892beadf2f8f0f88aa0942e7d225794379d62db42c6cf5`.
Se conservan también las dos capturas. No se recibió notebook ejecutado;
no se atribuyen salidas a un archivo no recibido.

Código: `b091785cd7b4a08ddcc0a7a79771cc88f1eb18da`.
Payload SHA256: `9bb9efde1f8e1a4b235136ba2590e059d3c902986d6eb16946f5e8a04a042130`.
Los 28 archivos del manifiesto verifican su hash. Manifiesto y contenido de cada
archivo son idénticos al paquete local del mismo commit; los bytes del contenedor
ZIP pueden diferir entre plataformas/compresores sin cambiar sus miembros.

## Causa primaria

`deployment16_install.log` muestra `ResolutionImpossible`: se solicitó
`huggingface-hub==0.36.2`, pero Gradio 6.32.0 exige `>=1.16.0,<3.0`. La combinación
fijada por nuestra preparación era imposible. Haber construido la interfaz en
un entorno con otras dependencias no demostraba instalabilidad del conjunto ML.
No es fallo de clave, cuota, datos ni respuestas del modelo.

La celda de instalación se detuvo antes de fuentes/GPU/tests. Después se ejecutó
la celda de construcción/inferencia. El empaquetado pudo terminar porque no
carga ML; el preflight falló al consultar metadata de `chromadb`, que no se había
instalado. Ese `PackageNotFoundError` es secundario y ocurrió antes del bloque
que guardaba metadata. No hay `requests.jsonl`, respuestas ni inferencias
contractuales producidas. No se afirma que la prueba ni la instalación aprobaran.

## Corrección 17

- Gradio **6.16.0** tanto en requirements como en `sdk_version`; conserva Hub
  0.36.2, Transformers 4.57.6, modelos, corpus, adaptador, prompts y FP16.
  Metadatos oficiales consultados: [Gradio 6.16](https://pypi.org/pypi/gradio/6.16.0/json)
  y [Gradio 6.32](https://pypi.org/pypi/gradio/6.32.0/json).
- Verificación de versión y requisitos cruzados antes de cargar pesos.
- El notebook nuevo bloquea inferencia si no acabaron instalación/GPU/pruebas.
- El preflight guarda metadata incluso si faltan paquetes o falla el payload.
- Se retira `run_history`, parámetro ausente en la API 6.16.0; se mantienen
  límites, limpieza de caché, rutas bloqueadas, errores sanitizados y telemetría
  sin contenido del usuario. No se instala con `--no-deps` ni se altera el
  conjunto ML para forzar la resolución.

Instalación local real Gradio 6.16.0 + Hub 0.36.2 + Pillow 11.3.0 realizada;
`pip check` sin dependencias rotas en ese entorno de interfaz. No representa
una instalación completa Linux/ML ni una prueba CUDA o ZeroGPU. Prueba T4 17
pendiente; main y Space de infraestructura sin cambios.

Regresión local de la corrección: **310 pruebas final + 128 M3 = 438 aprobadas**.
Cinco pruebas nuevas comprueban el conflicto original, ausencia de metadata,
coherencia requirements/SDK/control de entorno y conservación de fallos tempranos.
Las 18 pruebas del candidato también pasan con Gradio 6.16.0 instalado realmente.
No se interpreta este resultado como aprobación de inferencia real.
