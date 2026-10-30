# Desarrollo v4: regresión observada, no configuración final aprobada

Corrida del 29/10/2026 06:01–06:08 UTC (01:01–01:08 Colombia), Tesla T4. [ZIP original](contractrisk_m3_desarrollo_v4_resultados.zip), [notebook ejecutado](ContractRisk_M3_Desarrollo_v4_Colab_Ejecutado.ipynb). Hashes de código coinciden con el paquete entregado; contextos coinciden con offsets del corpus. 50 pruebas unitarias pasan y no hay error de celda. No hubo uso de gold final.

## Resultado técnico por caso, no accuracy

| Variante | Primer intento válido | Salida final válida | Mediana por consulta, segundos |
|---|---:|---:|---:|
| Control sin RAG | 7/8 | 8/8 | 2.359 |
| Denso | 1/8 | 4/8 | 9.831 |
| Avanzado | 1/8 | 3/8 | 11.738 |
| Agente | 1/8 | 1/8 | 15.027 |

10/32 válidas inicialmente y 16/32 tras un máximo de un reintento. Son 54 intentos de respuesta en total, ninguno alcanzó 512 tokens. V3 obtuvo 18/32 salidas válidas: v4 no mejoró la validez global. No confundir formato válido con sustento o acierto. El cambio incluyó prompt, límite y controlador: no atribuir toda variación a una única causa.

## Fallos y mejoras delimitadas

- El modelo copia literalmente `ID exacto del fragmento` del ejemplo de formato: el ejemplo introdujo un marcador que el modelo trató como cita. Tras reintento, frecuentemente omite abstencion. No es truncamiento en esta corrida: los registros muestran EOS antes del límite.
- Las dos llamadas necesarias se realizan correctamente en el primer paso y finalizan con tool_success. Los resultados de herramienta siguen siendo 75233920 COP y 226596000 COP. La respuesta del primer cálculo reproduce el valor correcto pero omite abstencion. La del segundo escribe 22659600 COP aunque la operación en explicación contiene 226596000 COP. No se debe completar automáticamente el booleano ni corregir el número para contarlo como acierto.
- En las seis preguntas que no necesitan cálculo, el agente intenta dos llamadas inválidas y termina por repetición bloqueada. Inventa segundo ID (p. ej. prefijo CO2 o número vecino); los controles impiden consultar esos argumentos. No existe todavía una decisión válida de no usar herramienta.
- Denso y avanzado siguen inventando cláusulas/auditorías a partir de campos de ficha. Incluso el control que se abstiene sobre multas afirma sin evidencia que la cláusula está en el contrato: la explicación también debe revisarse.
- La compactación eliminó la copia masiva observada en v3, pero el formato y la semántica no quedaron resueltos. Los tests unitarios acreditan reglas de software, no la obediencia del modelo.

## Decisión posterior

No repetir la misma configuración ni seguir alargando prompts sin un control experimental. Conservar v4 como diagnóstico. Preparar una prueba pequeña, separada del gold, que contraste cumplimiento de esquema, selección de herramienta/no herramienta, abstención y fidelidad numérica. Revisar el mensaje de reparación (debe mostrar esquema completo sin marcadores ambiguos) y considerar un generador alternativo, verificando compatibilidad y recursos antes de fijarlo. Si se cambia el generador, usarlo en las cuatro filas de la comparación final y declarar el cambio; no comparar filas finales con modelos distintos como efecto puro de RAG.

No prometer mejora por tamaño de modelo ni esconder errores con posprocesamiento de respuestas. Calibración del juez, dominio/RAGAS y ejecución final siguen pendientes. Un experimento académico puede informar resultados negativos; no requiere fingir un sistema sin errores, pero sí completar medición y evidencias. Main permanece sin cambios.
