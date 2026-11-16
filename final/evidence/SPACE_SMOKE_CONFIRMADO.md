# Prueba inicial del Space confirmada por capturas

Fecha: 16/11/2026. Fuente: cuatro capturas aportadas por el titular en la conversación de trabajo. No se recibió la clave W&B ni se afirma inspección autenticada del dashboard por el agente.

Space: https://huggingface.co/spaces/Juanoff/contractrisk-colombia

## Observado

- La interfaz de infraestructura responde al botón de salud: `status=alive`, `phase=infrastructure_only`, modelos e índice no listos. El `wandb_status=not_tested` corresponde a la consulta previa a los botones de registro, no es por sí mismo un error.
- Prueba técnica: evento con `success=true` y `wandb_status=queued_check_dashboard`. No registra pregunta, imagen ni OCR.
- Prueba GPU: `tensor_check=true`; dispositivo reportado `NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 2g.48gb`; duración de operación aproximadamente 0,01876 s. Este valor no incluye toda la experiencia de cola/servidor ni representa latencia de inferencia contractual.
- W&B muestra el proyecto `contractrisk-final` con una ejecución. Visibilidad observada: Team. La captura de lista demuestra creación de proyecto/run; no muestra las series de métricas, que deben inspeccionarse dentro del run.
- El evento reporta `version=1e5e401`, anterior a la corrección de arranque `cbe985a`. Es una variable declarativa desactualizada, no prueba de que el código antiguo esté ejecutándose. Corregirla sin borrar el evento histórico.

## Alcance pendiente

La asignación GPU de infraestructura está verificada. No se cargaron clasificador, generador, visión, embeddings, reranker ni índice del sistema integrado. La observabilidad de peticiones reales, los valores de métricas en W&B y el acceso del evaluador siguen pendientes.

La visibilidad Team no garantiza acceso externo. La guía permite enlace o capturas para W&B: configurar acceso apropiado o conservar capturas legibles de métricas reales sin información personal. No convertir en públicos otros proyectos ni credenciales.
