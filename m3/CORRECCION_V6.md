# Corrección candidata v6: abstención y contraste del juez

Implementada el 29/10/2026, todavía sin validación de inferencia real. No sustituye ni altera resultados v5, gold, main o rúbrica final.

## Hipótesis y cambios

V5 muestra que esquema válido no evita responder con campos irrelevantes ni inventar auditorías. El juez también confunde lo que está en la fuente con lo que dijo la respuesta. V6 enfatiza abstención sin contenido sustituto, diferencia entre campo y documento, necesidad de ambos operandos y copia de resultados verificables. El controlador especifica que `answer` no contiene IDs extra, un fallo observado en tres consultas v5.

El juez v6 debe citar literalmente la respuesta y contrastarla antes de emitir su puntuación. Se conserva la rúbrica semántica 1–5; cambia el protocolo, registrado como `m3-judge-1.1-contrast-candidate`. Una discrepancia de transcripción se registra como `quoted_answer_matches=false`, pero NO cambia la nota ni dispara reintentos. Esto permite detectar confusión sin fabricar resultados. Se mantienen ambas condiciones de verbosidad y los 12 pares; una puntuación alta equivocada se conserva.

## Prueba acotada

Se reutilizan exactamente preguntas/contextos recuperados de las 32 filas de desarrollo v5. El agente vuelve a decidir y ejecuta el cálculo sobre el snapshot. Los resultados antiguos no se envían al modelo. No se reconstruye recuperación: se aísla la modificación de instrucciones. Los tiempos de esta prueba NO deben incorporarse a la tabla final de latencia RAG.

Modelos: mismo Qwen2.5-3B-Instruct y revisión que v5, generación greedy, semilla 42. El juez comparte modelo, por lo que persisten riesgos de errores correlacionados. Ninguna regla transforma un resultado incorrecto en correcto; los tests locales comprueban este contrato, no que el modelo vaya a obedecer.

## Revisión obligatoria tras Colab

- Comparar 32 respuestas con v5: modalidades, dos cifras exactas, citas a ambos operandos, abstención de cláusula/auditoría y contradicción entre respuesta y bandera.
- Revisar todas las decisiones del agente, incluidas llamadas innecesarias, rechazos y máximos de pasos.
- Revisar `wrong_0` (Compraventa, explicación vacía) y `wrong_2` (120000 frente a 12000), razones y transcripción literal; reportar cualquier falsa aprobación.
- Recalcular y reportar 12 pares antes/después, cobertura y fallos. No afirmar mitigación por umbral arbitrario ni ocultar regresiones.
- Si persisten fallos, declarar límites y decidir explícitamente si se requiere otro evaluador; no convertirlo en reglas 4/1 ni ajustar contra gold.

Después: completar las métricas del harness y RAGAS, congelar configuración y ejecutar la comparación final. Esta prueba no cierra esos bloques.

## Ejecución

Notebook `ContractRisk_M3_Correccion_v6_Colab.ipynb`; ZIP generado mediante `git archive --format=zip --output=contractrisk_m3_correccion_v6_codigo.zip HEAD m3`. Sesión T4 nueva; ejecutar en orden; guardar ZIP de resultados y notebook ejecutado aun si hay error. No subir de nuevo el ZIP de código a Git.
