# Corrección 02 — prueba enfocada completada

16/11/2026, 18:46:17–18:56:03 UTC, Tesla T4. Código `8cda4e8fae6554447e04c6e2e0b1200035ee5d70`. [ZIP original](original_results.zip), [notebook ejecutado](executed.ipynb), [comprobaciones](audit.json). Archivos conservados sin editar; no se regeneraron respuestas en la auditoría.

Se comprobó CRC del ZIP, 11 registros, hashes de ocho fuentes contra el commit, cuatro imágenes contra manifiesto y corpus contra metadata. Las fuentes de las celdas del notebook coinciden con el original; cinco celdas ejecutables tienen salidas y ninguna salida de error. Los logs registran 32 pruebas final y 128 M3 aprobadas. El escaneo limitado de patrones de tokens no encontró coincidencias; no garantiza por sí solo ausencia de toda información sensible.

## Resultados observados

| Etapa | Resultado |
|---|---|
| Lectura visual nueva | Las tres fichas legibles producen ID, objeto, modalidad y monto concordantes con las líneas de referencia del manifiesto. Incluye una variante de contraste del mismo contrato; no son tres contratos independientes. |
| Imagen uniforme | Bloqueada por `uniform_pixels`, sin llamar al VLM. No se atribuye este acierto al modelo ni demuestra detección general de ilegibilidad. |
| Modalidad textual | Mínima cuantía, cita `CO1.PCCNTR.1180445::full_record`, cero llamadas a herramienta/router. |
| Diferencia textual | Una llamada válida; `abs(77000000 - 1766080) = 75233920 COP`, explicación y dos citas concordantes. |
| Auditoría ausente | Abstención por `absent_source_type`; control determinista de alcance, no juicio autónomo demostrado. |
| Orquestación de tres lecturas legibles | Responde modalidad/monto correctamente; cita imagen y ficha. La variante de contraste produce la misma respuesta. |
| Orquestación de imagen uniforme | Abstención sin inventar importe. |

`exceptions=[]`, `visual_schema_valid=4`, `valid_model_reads=3`, `vision_model_calls=3`, `uniform_pixel_guards=1`. El 4/4 de esquema incluye una salida de guard: no es accuracy del VLM. La lectura de modalidad/monto es correcta en esta muestra pequeña; no es evaluación estadística de extracción ni aprobación humana del gold final.

## Límites y pendientes

- Las imágenes son representaciones sintéticas de fichas públicas, no capturas reales ni contratos firmados. Los dos contratos ya se usaron en desarrollo y las correcciones fueron post-hoc.
- La lectura visual se ejecuta primero y luego se reutiliza: las latencias posteriores no son latencia multimodal fresca de punta a punta. Tampoco son una comparación de eficiencia.
- W&B estuvo **desactivado**. La primera celda informa que el secreto no fue accesible. Evidencia local completa, pero esta corrida no prueba registro remoto. En la siguiente sesión verificar nombre exacto `WANDB_API_KEY` y permiso de acceso del notebook en el panel de secretos, sin mostrar su valor.
- M1 no se repitió. Esta prueba no prueba carga simultánea de producción ni el funcionamiento del Space contractual; el Space sigue en infraestructura inicial.
- `quality_approved=false` se conserva. La auditoría técnica del asistente no sustituye revisión humana ni calibración del evaluador.

## Siguiente paso

Preparar diez candidatos visuales con cinco fichas distintas, dos pares de invarianza y controles de campo ausente, entrada vacía e instrucción maliciosa. Revisión humana y cierre de criterios antes de inferencia comparativa. No modificar prompts a partir de resultados del conjunto final sin versionar y declararlo.
