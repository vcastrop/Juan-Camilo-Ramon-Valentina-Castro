# Piloto literal 05 y corrección del evaluador 1.1

Auditado el 18/11/2026. Código original `6ec8dcdf22433c632b5eb0e5539401c33b9c923d`. [Auditoría](audit.json): 15 archivos fuente coinciden, mismo contenido del notebook publicado, sin errores de celdas, resumen original recalculado idéntico. Los logs muestran 122 pruebas final y 128 M3. Originales conservados sin editar.

Tesla T4, Qwen3-8B NF4, 252 capas Linear4bit verificadas. Siete generaciones completas con template nativo, sin truncamiento. Estado original `completed_pilot_failed`; dos casos no ejecutados y ninguna regresión completa. W&B `11gfx1rb` finalizó según logs; dashboard no verificado.

| Caso ejecutado | Nota original |
|---|---:|
| short_good | 5 |
| short_bad | 2 |
| number_bad | 1 |
| conflict_good | 4 |
| conflict_bad | 2 |
| empty_explanation_bad | 2 |
| citation_bad | 2 |

Todas están en su rango aprobado. El bloqueo se produjo porque el evaluador exigía que el juez usara exclusivamente fragmentos ya citados por la respuesta. En citation_bad, el juez puso 2 al identificar la cita incorrecta y mostró también el fragmento correcto disponible pero no citado por la respuesta. El programa lo marcó `respuesta:unknown_or_uncited_chunk`. Esa regla confundía evidencia diagnóstica del juez con respaldo realmente citado por la respuesta.

La versión **del evaluador** 1.1 permite un fragmento disponible no citado solo si se declara contradicción/incompletitud/insuficiencia y se marcan las citas como no respaldadas. Sigue rechazando fuentes desconocidas, citas no literales, rótulos ausentes y uso de un fragmento no citado para declarar respaldo. No cambia fuentes, citas de la respuesta, notas, motivos, modelo ni instrucciones. No es una validación ciega: la regla se corrigió después de inspeccionar el fallo. El estado original permanece como fallo del protocolo original.

[Recálculo CPU](replay_1_1.json): las siete notas y salidas se conservan; ninguna activa ahora un error automático. El piloto de nueve **sigue incompleto**: attribution_bad y accusation_good no ejecutados. No se prueba verbosidad ni calibración completa con este prefijo.

Persisten límites semánticos: short_bad marca acusación sin que haya acusación de irregularidad; en citation_bad el texto sin nombre no contradice por sí mismo la entidad. La ausencia de error programático no garantiza buena explicación del juez. [Continuación verificable](../../JUEZ_CONTINUACION_06.md): reutilizar todo el prefijo, completar solo lo pendiente y auditar razones; no regenerar para elegir notas favorables.
