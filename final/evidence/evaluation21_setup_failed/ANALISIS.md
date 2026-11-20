# Evaluación21: detención en preparación, no en API

Original ZIP SHA-256: `15b0bbf5851f4eda8f02e41842e5c394fba34f4fe460442cf31419c0c3a28011`.
Notebook SHA-256: `5bfd5f58980ebf4380b74c02587dc329c5e1e30330cad00ea4e457f9f733d2a2`.

La corrida del commit 7dd09bb se detuvo en setUpClass: el hash se calculó sobre
el checkout Windows CRLF y se comparó con el archivo LF de Git/Colab. El contenido
JSON no cambió. Los 339 tests restantes se ejecutaron, pero la suite falló por
este error; no se presenta como suite aprobada.

El ZIP conserva únicamente logs de historial, instalación y pruebas y el commit.
El notebook tiene una sola excepción en preparación y la celda API sin ejecutar.
No hay metadata de ejecución ni llamadas API en esta corrida, ni nuevas notas.
No modifica el registro de gasto previo ni autoriza liberar reservas anteriores.

Corrección: verificar el SHA de los bytes LF comprometidos en Git normalizando
solo CRLF→LF. Se mantienen las mismas decisiones, plan, rúbrica, respuestas,
umbral y presupuesto. Una prueba acepta ambos finales de línea y rechaza
cualquier adición de contenido. No se ignora ni desactiva el chequeo de integridad.

Tras corregirlo pasaron localmente 351 pruebas final y 128 M3: 479 en total.
Se comprobó igualdad exacta con el plan congelado; las pruebas API usan transporte
simulado, no gasto real. La ejecución Colab corregida aún debe recibirse.

Continuación: actualizar el checkout en el mismo Colab y repetir preparación.
Solo tras preparación aprobada ejecutar la celda API por primera vez. Si aparecen
marcadores/resultados previos en Drive, detenerse: no borrarlos ni repetir gasto.
