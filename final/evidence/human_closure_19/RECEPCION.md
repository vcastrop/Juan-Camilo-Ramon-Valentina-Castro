# Recepción de cierre humano — 19/11/2026

Revisor declarado en ambos archivos: Juan Camilo Ramon Perez, fecha 2026-11-19.
Originales conservados sin modificar:
[motivos del juez](original_judge_review.md) y [ocho dudas](original_domain_closure.md).

SHA256 motivos: `c71e52e60164cc741e0a7937ffb14e25c71d95b24375413aff52bbb9ad975d37`.
SHA256 dudas: `5e03e5e0dfc0a14feaea084cae9830ec1472dfc1af32de24dffa9c12aa742ab6`.

## Motivos: aceptación condicionada comprobada, no edición de la revisión

Once motivos de confirmación tienen SI. `confirm_empty_bad` tiene DUDOSO con una
condición expresa: «Si la rúbrica la contiene, el motivo es aceptable (SI)».
La regla sí estaba, antes de las corridas, en `final/judge_final.py`, tanto en
RUBRIC[2] como en BASE_SYSTEM: **«Sin explicación, nota máxima 2 aunque la respuesta
corta sea correcta»**. Los hashes de las corridas 12 y 13 corresponden a esa misma
rúbrica `88fa619df49d2db79f61e336312c6c38fe01b849763bec2b7a72c28b23648ec7`.
No se añadió el tope después de ver el resultado, ni se aplicó un ajuste en código:
el juez devolvió el 2 original.

Se añade la [rúbrica completa legible](../../RUBRICA_JUEZ_FINAL.md) que faltó
incluir en el paquete, sin modificar sus anclas. La recepción reproducible queda
en [derived_receipt.json](derived_receipt.json), separada de los dos originales.

La recepción derivada conserva `declared_decision=DUDOSO` y registra
`effective_decision=SI` únicamente bajo esa aceptación condicional explícita y su
evidencia. La misma condición cierra la salvedad de `empty_explanation_bad` en el
anexo. No se firma ni cambia el documento del usuario en su nombre.

El usuario declara leído el anexo de 38 motivos y marca SI con límites que se
conservan íntegros: errata `SYNHT::ficha`, diferencias de longitud antes del control,
prueba basada en repetir frases (no explicaciones largas legítimas), tolerancia
a respuesta repetitiva con contenido equivalente y omisiones menores de tildes.
No se transforma esto en ausencia general de sesgo ni calidad de redacción óptima.

Estado derivado: **juez aceptado para esta tarea y configuración congelada, con
límites documentados**, tras calibración, confirmación y revisión humana. No es
corrección del producto, garantía universal ni permiso de gasto adicional. Las
metadatas originales `judge_validated_for_final=false` se conservan como estado
anterior al cierre; el estado posterior está separado en esta recepción.

## Ocho dudas: once criterios adjudicados, sin rehacer las 44 revisiones

Se sustituyen únicamente los once valores DUDOSO por las decisiones del archivo:

| Caso | Decisión recibida |
|---|---|
| FP16 m3_004 | Respuesta y explicación respaldadas: SI; paráfrasis de la entidad aceptada. |
| NF4 m3_005 | Completa: SI considerando toda la salida estructurada, incluida explicación. |
| FP16 m3_006 | Críticos: NINGUNO; conserva NO en respaldo por el topónimo mal transcrito. |
| FP16 m3_009 | Críticos: NINGUNO; conserva NO en explicación por invertir el orden de fechas. |
| NF4 m3_009 | Explicación y completitud: NO; críticos NINGUNO según interpretación declarada del revisor. |
| FP16 y NF4 vis_04 | Abstención adecuada para la tarea: NO; se reconoce protección prudente, pero tarea no resuelta. |
| FP16 vis_05 | Explicación: NO; respuesta visual correcta, justificación en snapshot insuficiente. |

La condición comentada para m3_005 no se convierte en un criterio nuevo: el
protocolo de dominio previo pide completitud **semántica** de la salida, no solo
coincidencia literal en `respuesta`. La cobertura automática sí mira solo ese
campo y permanece independiente; no se recalcula para favorecer esta decisión.

Resultado: cero dudas en estas 44 anotaciones. Siguen el fallo crítico nuevo de
NF4 en m3_001 y las dos regresiones de invarianza; **NF4 continúa vetado para
despliegue**. No se declara FP16 correcto en todos los casos ni se calculan aún
tasas finales de dominio sin las notas reales del producto.

## Próximo bloqueo: presupuesto de aplicación

Plan offline preparado para los cinco perfiles × 22 casos = 110 salidas guardadas,
sin regeneración ni gold en el payload del juez. Incluye las siete salidas con
estructura inválida; no las oculta ni les inventa una nota LLM.
Techo autorizado intacto: USD 5. Acumulado estimado/reservado USD 4,1974125;
margen local USD 0,8025875; reserva por petición USD 0,6144. No iniciar la corrida
completa sin decidir presupuesto. La ilustración basada en los 49 juicios nuevos
anteriores arroja USD 1,117824 adicionales para 110, pero no es una previsión ni
garantía: los contextos del producto son diferentes. Se necesita conciliación
verificable de consumo o autorización explícita de otro techo total; no se borran
reservas desconocidas, no se baja silenciosamente el límite del juez y no se
presenta una muestra como evaluación completa. Esta recepción no hace llamadas.
