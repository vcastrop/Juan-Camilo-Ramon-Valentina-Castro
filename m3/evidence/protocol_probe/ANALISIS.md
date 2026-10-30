# Prueba controlada de protocolo y modelo — decisión de integración

Corrida T4 del 29/10/2026 06:30–06:36 UTC (01:30–01:36 Colombia). [ZIP original](contractrisk_m3_protocolo_resultados.zip) y [notebook ejecutado](ContractRisk_M3_Prueba_Protocolo_Colab_Ejecutado.ipynb). Los hashes del código coinciden con el paquete entregado; cases.json coincide con su hash; las comprobaciones mecánicas se recalcularon sin diferencias. 30 registros, 56 tests aprobados, sin errores de celdas ni de ejecución de modelos. No se ejecutó el gold.

## Resultados de los casos sintéticos

| Modelo/protocolo | Formato inicial | Formato final | Comprobación mecánica de respuesta | Selección herramienta/no herramienta |
|---|---:|---:|---:|---:|
| 1.5B / v4 | 2/6 | 6/6 | 5/6 | 2/4 |
| 1.5B / v5 | 1/6 | 1/6 | 1/6 | 2/4 |
| 3B / v5 | 6/6 | 6/6 | 5/6 | 4/4 |

Formato no equivale a exactitud. Mechanical pass tampoco evalúa íntegramente las explicaciones. V5 no mejoró al modelo pequeño; no se puede atribuir el avance al nuevo prompt por sí solo. Bajo v5, 3B supera a 1.5B en esta prueba limitada. No se probó 3B/v4 ni se concluye cuál sería su resultado.

La memoria GPU máxima asignada registrada fue 3239568896 bytes para 1.5B y 6415865856 para 3B (no consumo total del dispositivo). Ambas cargas se completaron. Las medianas mixtas de respuestas y enrutamiento son 3.295, 6.036 y 5.371 segundos respectivamente; no equivalen a latencia del RAG final. Los tiempos incluyen reintentos cuando existen.

## Revisión de contenido

- 3B/v5 distingue las dos modalidades de Compraventa, cita los fragmentos y reproduce correctamente 7050000 y 241500000 COP con sus operaciones.
- 3B/v5 elige answer para modalidad y auditoría, y tool con los IDs correctos en ambos cálculos. Aquí se probó la decisión aislada, no el bucle completo con recuperación real.
- 3B/v5 falla en absence_990004: responde estado y valor como si fueran texto de una cláusula de multas, pese a que la fuente sintética dice que no incluye clausulado. No se corrige ni se cuenta como acierto.
- En absence_990003 usa abstencion=true y explica que no hay informe, pero empieza con “No se concluyó una auditoría específica”. Esa afirmación puede exceder la evidencia: ausencia de informe en fuentes no prueba inexistencia de auditoría. El control mecánico la acepta; la revisión semántica registra esta reserva.
- 1.5B/v4 inventa que auditoría concluyó estado Cerrado y su explicación de ausencia de cláusula es contradictoria. 5/6 mecánico no debe presentarse como cinco respuestas plenamente sustentadas.

## Decisión y pendientes

Adoptar **3B/v5 como candidato de integración**, con revisión `aa8e72537993ba99e69dfaafa59ed015b17504d1`. Es una decisión de desarrollo basada en formato inicial estable, decisiones correctas y cifras fieles; no certifica robustez general. Preservar los resultados negativos de todas las condiciones.

Siguiente bloque: integrar el mismo generador y protocolo en las cuatro variantes (control sin RAG adaptado a QA, denso, avanzado y agente); validar con las preguntas reales de desarrollo antes de congelar la configuración final. No rellenar abstenciones ni sustituir salidas a partir del gold. Conservar el fallo de clausulado como limitación explícita, sin modificar el caso final para facilitarlo.

Completar además calibración independiente del juez, prueba multicaso de verbosidad, métricas de dominio y RAGAS; luego ejecutar cuatro filas con el mismo gold y configuración. Si juez/generador comparten familia, declarar ese riesgo; independencia del indicador de acierto no equivale a independencia de modelo.

La prueba sintética no evalúa recuperación, contratos reales, el agente completo ni cumplimiento total de la entrega. Main y gold no se modificaron.
