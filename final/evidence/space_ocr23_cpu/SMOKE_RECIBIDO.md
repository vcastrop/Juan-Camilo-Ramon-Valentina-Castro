# Siete rutas funcionales reales — evidencia aportada por el usuario

Versión única5b42adc35d6e3225c93dfbda13ae2e1730bad1c8. El usuario ejecutó cada
caso una vez en la interfaz HF y envió resultado, evento técnico y captura.
Esta tabla transcribe campos de sus mensajes; no es un ZIP bruto de servidor
ni una evaluación independiente/ciega. No se hicieron nuevas llamadas aquí.

| Caso | Hora UTC20/11/2026 | request_id | Latencia servicio s | Resultado observado |
|---|---|---|---:|---|
|1 texto/modalidad|02:45:57.170134|99daad02-dec8-497a-b6f2-7bb359dc6b7e|4.09395526399021|Mínima cuantía; cita full_record1003124; RAGtrue, herramientafalse.|
|2 cálculo|02:48:47.260720|f39ccd4c-ffdd-4c32-aad7-a0e0c4c4decb|5.756941851985175|4.391.824 COP = abs(64.992.574−60.600.750); dos fuentes tool_value; RAG/tool/routertrue.|
|3 imagen legible|02:50:46.073418|d96c6779-5469-4607-b1fa-82df52e8d96f|4.459175617987057|Mínima cuantía/60.600.750 COP; IMAGE::input y full_record1003124; OCR y RAGtrue.|
|4 valor ausente|02:53:30.594793|40b758fc-d5a8-4b32-8b5d-91791487927e|0.7827919349947479|Abstención, missing_visual_fields, fuentes/citas vacías; OCRtrue, RAGfalse.|
|5 blanco|02:56:35.141113|a30200cc-7661-47d4-8f49-5e671e26caf8|0.0014085769944358617|Abstención, unreadable, fuentes/citas vacías; OCRtrue, RAGfalse.|
|6 auditoría sin fuente|02:58:55.409571|84603007-a660-4427-a448-0b05b3be0e7b|0.000504135008668527|Abstención, absent_source_type, fuentes/citas vacías; no RAG/generación necesarios.|
|7 M1|03:00:43.836999|b496f6bd-e569-45a0-a738-41822e2f46a8|0.039165898982901126|SUFICIENTE; confidence0.9883918166160583; confidence_calibratedfalse; classifier_usedtrue.|

Los siete eventos declaran successtrue, error_codenone y components_knowntrue.
Todos devuelven queued_check_dashboard: prueba de encolado, no de sincronización
W&B ni de acceso del evaluador. Las latencias son internas del servicio: no
incluyen cola, asignación GPU ni red; no se presentan como rendimiento estadístico.

## Lectura y límites

- Casos1–3 respaldan funcionamiento real de recuperación, herramienta y OCR
  dentro de estos ejemplos; no se extrapolan a todas las consultas.
- La explicación1 añade tipo de contrato correcto aunque no solicitado.
- Caso3 conserva explicación genérica "el documento proporciona"; imagen y
  snapshot concuerdan. No demuestra autenticidad.
- Caso4 evita completar desde el corpus un valor ausente de la imagen.
- Caso5 protege con abstención, pero "captura más clara" no distingue blanco
  de borroso: limitación editorial real, no corregida ni reejecutada.
- Caso6 lo resuelve la guarda de tipo de fuente, no un razonamiento del LLM.
- Caso7 confirma ejecución M1 y su señal. No hay gold independiente para esta
  frase: no se presenta como nueva prueba de exactitud del clasificador.
  0.9884 no es probabilidad calibrada de suficiencia ni de ausencia de fraude.
- No es un benchmark nuevo7/7 de calidad, ni sustituye los22 casos de Colab,
  ni mide eficiencia o resistencia adversarial. Los fallos conocidos continúan.

Pendiente inmediato: salud posterior con real_request_verifiedtrue, comprobar
los siete eventos/version en la run W&B y acceso externo del Space y W&B.
