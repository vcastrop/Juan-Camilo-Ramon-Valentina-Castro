# Corrida 04: mejora observada, calibración rechazada

Auditada el 18/11/2026. Código `50281e90d3492f7b74bb70010f50b383f0c9efc5`. [Integridad y recálculo](audit.json): 13 archivos fuente coinciden, cinco celdas ejecutadas sin errores, mismo contenido fuente del notebook y resúmenes recalculados idénticos. ZIP y notebook originales preservados sin editar.

Qwen3-8B NF4 cargó en Tesla T4, 252 capas Linear4bit verificadas, sin offload. 38 generaciones nativas completas, sin truncamiento ni reajustes de nota. Los logs muestran **112 pruebas final y 128 M3** en aquella ejecución. Las cifras posteriores corresponden a versiones nuevas.

| Criterio | Observado | Exigido |
|---|---:|---:|
| Piloto | 7/7 | 7/7 |
| Juicios válidos | 38/38 | 38/38 |
| Principales en rango | 19/20 | al menos 18/20 |
| Malos principales con 4–5 | 1 | 0 |
| Diferencia máxima de verbosidad mitigada | 3 | máximo 1 |

Fallo principal: `attribution_bad` recibe 4; la cifra 73000 es correcta pero la explicación la atribuye falsamente al objeto. En `after_verbose/short_bad`, la confusión entre modalidad y tipo recibe 5 frente a 2 en su versión breve. La diferencia media absoluta de los seis pares es 1 antes y 1,1667 después: la mitigación no mejoró esta medida. Las comprobaciones de tres juicios contradicen sus notas según las reglas fijadas.

También hay defectos semánticos no resumidos por el 19/20: `conflict_bad` describe 8500 en lugar de 85000, y algunas verificaciones marcan acusación o abstención donde no corresponde. El acierto de rango no garantiza una justificación fiel. No se conserva texto privado de razonamiento; solo hashes/conteos y JSON finales públicos.

La run W&B `4cgy5vr6` finalizó según metadata/logs; acceso al dashboard no verificado. No se ejecutó confirmación separada, ni se aprobó juez o eficiencia. [Protocolo 05](../../JUEZ_RESPALDO_LITERAL.md) es una corrección posterior a inspeccionar esta evidencia; no una prueba ciega.
