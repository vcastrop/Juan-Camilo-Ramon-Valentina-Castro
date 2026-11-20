# Ruta de cierre con tres horas disponibles

**Actualización:** punto1 completado, no ejecutar más API. OCR20 tiene 22 notas,
media4,4545 y dominio18/22 auditados. El bloqueo prioritario es ahora punto2:
despliegue real OCR y comprobación pública/W&B. El resto del cronograma original
es orientativo y debe ajustarse al tiempo efectivamente restante.

Estado aproximado 76 %, no aprobación ni garantía de terminar. Desarrollo y
evidencia histórica están avanzados; publicación contractual sigue sin validar.
Se prioriza completar evidencia y acceso sobre nuevos experimentos.

1. **Calidad OCR, primero:** revisión humana recibida. Actualizar Colab21,
   ejecutar preparación corregida y por primera vez la celda API, máximo USD7
   TOTAL. Conservar ZIP/notebook incluso si falla, sin reintentos ni borrar Drive.
   Auditar notas y cruzar con revisión humana; reportar parciales si no termina.
2. **Despliegue, bloqueo principal:** preparar paquete OCR distinto del candidato
   VLM histórico. Arranque/health deben declarar cuatro modelos neuronales más
   Tesseract, sin fingir modelo visual cargado. Verificar texto, cálculo, imagen,
   dos abstenciones y M1 con modelos reales. Publicar solo ese paquete en el Space,
   probar desde fuera y comprobar eventos reales en W&B sin texto/PII ni claves.
   No subir el candidato VLM antiguo ni presentar infraestructura como producto.
3. **Reporte y acceso:** actualizar tabla del perfil nuevo sin sobrescribir los
   históricos, conservar resultado NF4 negativo, explicar OCR y límites, diagrama,
   roles reales y Uso de IA. Portada/README raíz con enlaces reproducibles,
   despliegue, evidencia y permisos de W&B comprobados.
4. **Presentación:** diapositivas para máximo diez minutos, demostración breve
   y plan de respaldo con evidencia guardada. No atribuir inmunidad adversarial
   al generador ni seguridad de producción.
5. **Cierre:** validar desde checkout limpio instrucciones/tablas/enlaces,
   revisar secretos/licencias, PR y merge autorizados sin pisar main; entregar
   los elementos exactos de la guía y guardar comprobante de Interactiva.

Distribución orientativa, no duración garantizada: primeros 20 min calidad;
20–90 min despliegue; 90–135 min reporte/accesos; 135–160 min presentación;
160–180 min auditoría/publicación/entrega. Si un bloqueo consume la reserva,
informar evidencia real y pendientes: no declarar 100 % por el plazo.

No abrir nuevas calibraciones, modelos, cuantizaciones o mejoras de calidad en
esta ventana. No repetir 17–20 ni las evaluaciones históricas para mejorar cifras.
