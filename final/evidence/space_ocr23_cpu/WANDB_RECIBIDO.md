# Run pública identificada; estado Crashed pendiente de diagnóstico

Enlace: https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/f7ljlxip
Nombre comic-valley-26. Capturas del usuario confirman job_type
public-contract-service, comando/app/app.py, Python3.12.12, W&B0.31.0,
phasecontractual_candidate y versión5b42adc35d6e3225c93dfbda13ae2e1730bad1c8.

El último summary coincide exactamente con el caso7 recibido: latencia
0.039165898982901126, success1, classifier_used1, resto de componentes0 y
abstention0. Las gráficas muestran latencias compatibles con los otros smoke:
esto confirma recepción de métricas en W&B a través de la sesión del usuario,
no solo encolado. Summary describe el último evento, no la media de la run.

## Pendientes no ocultados

La captura nueva indica **Crashed**, inicio19/11/2026 21:45:21 y runtime15m25s.
El estado cambió respecto a la captura Running anterior. W&B define Crashed
como ausencia de heartbeats del proceso interno; no demuestra por sí solo causa,
ni invalida los resultados almacenados ni confirma que el Space siga vivo.
No atribuirlo sin logs a mantenimiento, suspensión, cuota, modelos o red.
Fuente: https://github.com/wandb/wandb/blob/main/wandb/apis/public/runs.py

La curva success incluye eventos0 adicionales a los siete casos exitosos
recibidos. Deben clasificarse con los eventos JSON de Container logs; W&B
registra flags/latencia pero no request_id/error_code como métricas. No declarar
100% de éxito de toda la run ni borrar/recrear para ocultar ceros o Crashed.

Solicitar salud actual sin GPU y últimos Container logs desde03:00UTC20/11/2026,
sin reiniciar ni nuevas consultas. No pulsar Stop run ni cambiar versiones.
Acceso externo de Space/W&B continúa sin comprobación; sesión propietaria no basta.

## Actualización con logs y salud actuales

El usuario volvió a consultar salud: backendreadytrue, real_request_verifiedtrue,
cuatro modelos/índice/OCR listos, startup_errornull. No se demuestra una caída
del servicio contractual por el indicador Crashed de la run.

`container_smoke_original.txt` conserva el log aportado. `events_audit.json`,
reproducible con `final.audit_space23_logs`, identifica10 eventos distintos:
7 exitosos y3 rechazosinvalid_input. Dos QA sin consentimiento (02:45:19 y
02:45:26UTC) y uno M1 sin descripción/imagen (03:00:16UTC); los errores Gradio
adyacentes confirman esas razones. No hay runtime_error ni gpu_dispatch_error en
estos10 eventos. Los7 IDs exitosos coinciden con los resultados compartidos.

Estos rechazos accidentales muestran los controles de entrada, no una prueba
prospectiva adicional. No se borran: successtotal7/10 no es exactitud70%, y7/7
peticiones válidas no demuestra calidad general. Auditoría offline pasó su test.

El log no contiene un error explícito del proceso interno W&B posterior a M1.
El estado de conexión sigue sin verificarse; queued_check_dashboard es el último
estado local y no comprueba heartbeat. Causa de Crasheddesconocida, sin atribuirlo
a inactividad, cuota, reinicio o red sin datos del SDK/proveedor.

## Salud posterior recibida antes de estas capturas

El usuario envió JSON/capturas con contract_system_readytrue,
real_request_verifiedtrue, cuatro modelostrue, index_readytrue,
visual_reader_readytrue, startup_errornull y queued_check_dashboard.
Esto respalda funcionamiento tras las consultas en ese momento, no salud
posterior al estado Crashed observado ahora.
