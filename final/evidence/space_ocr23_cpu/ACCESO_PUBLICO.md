# Acceso sin sesión comprobado por el usuario

El usuario cambió la visibilidad del proyecto W&B a **Public**, no Open. La
captura posterior sin sesión muestra Log in/Sign up y las gráficas de la run:
https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/f7ljlxip
El404 anónimo anterior queda resuelto por permisos. El cambio afecta al proyecto
y sus corridas/archivos, no solo esta run. No se afirma revisión de privacidad
exhaustiva de las26 corridas por haber publicado el proyecto.

El usuario también abrió en incógnito, sin sesión:
https://huggingface.co/spaces/Juanoff/contractrisk-colombia
La interfaz y el botón de salud respondieron con versión
5b42adc35d6e3225c93dfbda13ae2e1730bad1c8, contract_system_readytrue,
real_request_verifiedtrue, generator/classifier/embedding/rerankertrue,
index_readytrue, visual_reader_readytrue y startup_errornull. Tesseract5.5.0,
spa/eng con los hashes de referencia. W&Bstatusqueued_check_dashboard.

Fuente: capturas y JSON aportados en el chat; comprobación externa hecha por el
usuario, no navegación de este agente ni nueva petición de inferencia anónima.
No se consumió GPU para la consulta de salud. No se extrapola a cuota disponible
para cualquier visitante ni disponibilidad permanente del proveedor.

## Qué queda resuelto y qué no

- Resuelto: lectura pública de la evidencia W&B y acceso a interfaz/salud HF.
- Ya documentado: siete rutas funcionales reales con propietario;10 intentos,
  siete válidos exitosos y tres entradas rechazadas por controles.
- No resuelto: run histórica W&B Crashed. Los datos son accesibles, pero se
  desconoce la causa de interrupción de heartbeat; no se finge estado Finished
  ni se declara monitoreo continuo estable. No bloquea leer evidencia guardada.
- Pendiente académico: portada final, reporte coherente con OCR/producción,
  diagrama, roles/IA confirmados, diapositivas/demo, reproducción/auditoría
  desde limpio, revisión de secretos/licencias y publicación/entrega autorizadas.
