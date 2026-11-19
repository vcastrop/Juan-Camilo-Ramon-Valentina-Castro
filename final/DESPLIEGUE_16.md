# Candidato público FP16 y verificación 16

Estado: **preparado, no desplegado ni verificado con modelos reales todavía**.
El Space de infraestructura y main permanecen sin cambios. No se repite la
evaluación de 110 respuestas ni se consume API del juez.

## Qué se reutiliza

Generador nativo Qwen2.5-3B FP16/512 tokens, Vision Qwen2-VL-2B,
recuperación híbrida con reranking y ficha completa, router/herramienta acotados
y controles visuales del perfil `integrated_fp16`. Sin cambiar prompts,
revisiones o decodificación. M1 añade el clasificador histórico CPU, separado
del benchmark QA. Revisiones en `config.py`; corpus/adaptador con SHA fijo.

`service_runtime.py` construye componentes reales; `service_contract.py` limita
entradas y separa resultado de metadatos; `service_telemetry.py` envía únicamente
metadatos tipados. `build_space_candidate.py` crea cuatro archivos en carpeta
nueva, vinculados a un commit y a un manifiesto por archivo. La plantilla no es
una aplicación lista para subir: el constructor inserta la verificación del ZIP.

## Comprobaciones locales

Pruebas con dobles de componentes: readiness exige cinco modelos e índice;
errores no se convierten en respuestas; router no implica herramienta exitosa;
límites/consentimiento; eventos con campos y tipos acotados; W&B sin captura de
consola/código; ZIP sin rutas escapadas, archivos extra o hashes incorrectos.
La interfaz se construye con Gradio 6.32.0 sin cargar Torch. Esto **no** verifica
pesos, calidad semántica, memoria real, disponibilidad o aislamiento de ZeroGPU.

## Prueba real en Colab

1. Abrir `ContractRisk_Final_Despliegue_16_Colab.ipynb` en una sesión nueva.
2. Seleccionar **Entorno de ejecución → Cambiar tipo → GPU T4**.
3. Ejecutar las celdas en orden. No necesita secretos ni pagos adicionales.
4. Conservar el ZIP descargado y descargar el notebook mediante
   **Archivo → Descargar → Descargar .ipynb**, con sus salidas.
5. Revisar ambos antes de subir archivos al Space. Si falla, la última celda
   descarga el parcial; no sustituir errores ni repetir buscando mejores respuestas.

La prueba carga el **payload generado**, no un segundo constructor experimental.
Incluye QA pública, M1, captura sintética, diferencia de dos contratos, fuente
ausente, imagen blanca y entrada inválida. Guarda respuestas de prueba para
auditoría local; **esto no es el log del servicio público**. No se cargan datos
privados ni se envían esas respuestas a W&B.

## Después de revisar la prueba

Verificar en ZeroGPU el arranque con `spaces` antes de CUDA, modelos preparados
al inicio e inferencia decorada. Solo entonces reemplazar los cuatro archivos del
Space (el antiguo `telemetry.py` ya no se importa; no hace falta borrarlo).
Verificar desde URL `/healthz`, `/readyz`, texto/M1/imagen/cálculo/abstención y
eventos reales W&B accesibles. `real_request_verified` no certifica acierto.
No usar las latencias ZeroGPU como comparación de cuantización de T4.

Revisar también la caché temporal de Gradio y el aviso de uso público, las
licencias del modelo y las restricciones de investigación no comercial. La
licencia Qwen se descarga desde la revisión oficial y se verifica por SHA; no
se atribuye Apache a Qwen2.5-3B. No hay fallback a NF4 ni API pagada en el servicio.
