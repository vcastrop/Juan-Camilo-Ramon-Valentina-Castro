# Juez 11 — recuperación con diagnóstico de transporte

Estado 18/11/2026: preparado y probado localmente con transporte simulado; **sin nuevas peticiones reales de este candidato**. [Notebook CPU](ContractRisk_Final_Juez_11_Recuperacion_Colab.ipynb). No regenera respuestas contractuales y no requiere T4.

## Por qué tiene sentido este intento controlado

Los intentos 07–10 están preservados. Hydrogen devolvió una nota válida 2; esa nota y su motivo se reutilizan, sin volver a pedirlos. La siguiente pregunta quedó sin nota, primero con 503 y luego con un error genérico de transporte/JSON. Ese código anterior no distinguía timeout, red o JSON inválido del sobre de la API. Este cliente sí los separa sin guardar mensajes sensibles.

No se cambia el juicio para buscar un resultado favorable: mismo modelo, instrucciones, schema, semillas, nivel de razonamiento, límite de salida, anclas, rúbrica y umbrales. Prueba de regresión confirma el mismo hash de la petición pendiente `attribution_good`.

## Cambios técnicos y límites

- Timeout de lectura 180 segundos en vez de 90, explícito en la política versionada. No se cambia el máximo de tokens de generación.
- Solo HTTP 503 sin nota admite **un reintento global**, tras 60 segundos. Si el proveedor pide más de 60 segundos, se detiene. No se reintentan timeout, red, JSON de transporte, otros estados HTTP ni una nota equivocada. La reparación de formato original sigue como máximo una por juicio.
- Se verifican los ZIP/hashes y que 10 no agregó una nota válida. Se conserva la nota de 09, los seis asientos del ledger y las cuatro marcas previas. Nueva marca exclusiva `hydrogen_calibration_resume_2.started.json`; si existe, no borrar para repetir.
- El registro anterior suma **USD 2,4706725 estimados/reservados**, no factura. Esta recuperación usa como sublímite el mismo techo TOTAL autorizado **USD 5**, incluidos todos los intentos previos. No son USD 5 adicionales. No se liberan reservas desconocidas ni se activa facturación.
- La configuración original y los archivos financieros históricos se conservan con sus valores anteriores; la política efectiva de esta continuación está en resume_policy.json y metadata.resume_policy. La modificación del sublímite es financiera/técnica, no un cambio de preguntas, generación o aceptación de notas.
- Cada envío de generación reserva su máximo antes de salir; el timeout/503 no reinicia el presupuesto. La vigencia de precios original continúa siendo obligatoria: si vence, se detiene antes de la petición.
- No hay claves en URLs, redirecciones, mensajes completos del proveedor, pensamiento privado ni claves en salidas. Se registran códigos/categorías sanitizadas y respuestas finales públicas del juez.

El acceso real del proveedor no está garantizado por estos tests ni por consultar su catálogo. Si vuelve a fallar, el objetivo es obtener un diagnóstico específico y detenerse, no iniciar otra serie de intentos sin límites.

## Ejecución del equipo

1. Abrir notebook 11 con CPU. No repetir 07–10 ni Comparación 02.
2. Habilitar los secretos existentes GEMINI_API_KEY y WANDB_API_KEY para este notebook. No pegar ni enviar claves.
3. Montar la misma cuenta y carpeta Drive que antes. No eliminar ledger, locks ni marcas.
4. Confirmar GRATUITO solo si el proyecto sigue sin facturación. Ejecutar en orden.
5. Guardar ZIP y notebook con salidas incluso si se detiene y enviar ambos. No activar pagos ni reiniciar por cuenta propia.

Si el piloto pasa, se completa la regresión con 37 juicios nuevos más uno reutilizado. Pasarla no significa que el juez ya esté validado: faltan auditoría de motivos y confirmación de doce casos aprobados. Esta corrida no califica las 110 respuestas reales ni sustituye su revisión humana.
