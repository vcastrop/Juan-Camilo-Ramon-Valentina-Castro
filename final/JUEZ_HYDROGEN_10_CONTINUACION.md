# Continuación 10: conservar respuestas y acotar indisponibilidad

Estado 18/11/2026: ejecutado, [resultado auditado](evidence/hydrogen_10/ANALISIS.md). Nota anterior intacta, 503 seguido de error de transporte/JSON en el reintento, cero notas nuevas. No repetir. Las instrucciones siguientes documentan la corrida histórica, no autorizan reiniciarla. [Notebook CPU histórico](ContractRisk_Final_Juez_10_Hydrogen_Continuacion_Colab.ipynb).

La [corrida 09](evidence/hydrogen_09/ANALISIS.md) produjo una nota válida 2 y luego HTTP 503. Se reutiliza esa nota sin regenerarla; la continuación empieza en `attribution_good`. Mismo modelo, instrucciones, semillas, rúbrica, referencias y criterios de aceptación. Se verifican los hashes del ZIP, los archivos originales del candidato, el catálogo del modelo y el registro persistente.

## Cambios técnicos y financieros, no de calificación

- Solo HTTP 503 sin respuesta admite hasta **dos reintentos en toda la continuación**, con espera aproximada de 30 y 60 segundos y ligera variación. No se reintenta una nota fuera de rango para buscar otra favorable. El único reintento de formato del protocolo original no cambia.
- No se reintentan otros códigos, errores de red, truncamientos ni cambios de modelo. Si el proveedor pide más de 60 segundos, se detiene. Un fallo conserva parciales.
- Cada nuevo envío de generación reserva su propio máximo conservador antes de salir. Las reservas de intentos sin respuesta siguen intactas.
- El sublímite acumulado de esta etapa se fija en **USD 3,50**, incluyendo el registro previo de USD 1,2418725. El techo total autorizado permanece **USD 5**. No se activa facturación, no se borra el registro y estas cifras no prueban cargos reales. Se amplía el sublímite de etapa antes de nuevas notas porque las reservas desconocidas de los 503 consumen margen.
- Se conservan códigos y categorías sanitizadas del proveedor, nunca el mensaje completo que pudiera repetir credenciales o entradas.
- El registro y marca exclusivos impiden reiniciar accidentalmente esta continuación. Si falla, enviar evidencias; no borrar marcas para repetir.

## Ejecución

1. Abrir el notebook 10 en Colab y seleccionar CPU; no necesita T4.
2. Permitir a este notebook leer los secretos existentes `GEMINI_API_KEY` y `WANDB_API_KEY`. No crear ni enviar claves nuevas.
3. Ejecutar las celdas en orden. Montar la misma cuenta y carpeta Drive que usaron 07–09; conservar todos los archivos de presupuesto.
4. Escribir `GRATUITO` solo si el proyecto sigue sin facturación activada. No pagar ni recargar para este ensayo.
5. Descargar el ZIP y el notebook con salidas, incluso si se detiene. Enviar ambos para auditoría. No repetir celdas de inferencia para buscar mejores notas.

Si pasa el piloto, se completan 37 juicios nuevos más el válido reutilizado: 38 en total, sin contar peticiones fallidas como juicios. Incluso si pasa la regresión, faltan revisión humana de razones y confirmación separada de 12 casos antes de aceptar el juez para la evaluación final.

HTTP 503 es compatible con indisponibilidad transitoria; no demuestra clave incorrecta. Hay una generación real válida con esa misma clave. Tampoco podemos atribuir todos los fallos a una causa concreta sin evidencia del proveedor. [Recomendación oficial de reintentos acotados](https://aistudio.google.com/docs/troubleshooting#retry-strategy).

Main y el Space no se modifican. El avance global permanece 40–45 %; ver [ruta pendiente](PROGRESO_FINAL.md).
