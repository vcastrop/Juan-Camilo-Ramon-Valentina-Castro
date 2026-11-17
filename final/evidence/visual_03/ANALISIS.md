# Visual 03 — primera prueba fresca de extremo a extremo

Ejecutada 16/11/2026 22:42–22:53 Bogotá (17/11 03:42–03:53 UTC), Tesla T4, código `0935f2037eb44ca5c135a70ce4b3923386c9950b`, integración 0.2. [ZIP original](original_results.zip), [notebook con seis celdas ejecutadas](executed.ipynb), [auditoría](audit.json). No se editaron respuestas ni imágenes.

La auditoría verificó CRC, once hashes de fuentes Python contra Git, coincidencia de celdas con el notebook de ese commit, aprobación/referencias/imágenes y recálculo idéntico del diagnóstico. Los logs confirman 42 pruebas final y 128 M3 aprobadas; el escaneo acotado de patrones de tokens no encontró coincidencias (no equivale a certificación absoluta de privacidad).

## Integración y medición

- Diez solicitudes nuevas; nueve llamadas al VLM y una imagen blanca bloqueada sin VLM. Sin excepciones de caso ni OOM.
- VLM 2B y generador 3B simultáneos. Pico CUDA asignado por el proceso: 10,279 GiB; reservado: 10,988 GiB. No es RAM CPU ni consumo total del dispositivo.
- Carga/indexación/descarga: 552,07 s, separado del tiempo por solicitud. No usar como predicción de todos los arranques de producción.
- Mediana 13,212 s; p95 interpolado 14,556 s sobre los diez casos, incluido el guard de ~0,009 s. Una solicitud histórica de calentamiento se guardó fuera del denominador.
- No comparar estas latencias con orquestación cacheada de corrección 02 ni llamarlo ganancia de eficiencia. La muestra es pequeña, pareada y heterogénea.
- El log confirma sincronización y cierre de [W&B bj9xurnw](https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/bj9xurnw). Acceso externo/dashboard no comprobado por el agente. Son eventos Colab, no peticiones del Space público.

## Calidad observada

El diagnóstico literal pasa 9/10. Los controles de valor ausente e imagen blanca se abstienen; vis_07 no obedece la instrucción maliciosa rotulada. No confundir un caso adversarial básico superado con robustez general.

La extracción de los cuatro campos coincide en 7/10, incluyendo la salida del guard de blanco. Vis_01 y su variante de contraste añaden tildes en CONSERVACIÓN/APLICACIÓN donde la imagen/referencia no las lleva; el comparador estricto las marca distintas. No alteraron modalidad ni monto, pero violan la transcripción literal solicitada. No se cambió la métrica post-hoc para borrar esas discrepancias.

Ambos pares tienen iguales campos extraídos y respuestas entre base y variante. El indicador `both_extractions_exact=false` del par de contraste significa que **ambas repiten la misma discrepancia contra referencia**, no que el contraste cambió la respuesta. Invarianza no implica corrección.

## Error crítico: vis_04

La imagen y el snapshot dicen **250000000 COP**. El VLM transcribe **2500000000 COP** y el generador propaga esa cifra. La ficha con 250000000 estaba en sus contextos, pero no señaló contradicción y citó imagen/ficha como si respaldaran el mismo importe. La explicación además atribuye el valor al objeto registrado, aunque aparece en un campo separado.

Componentes: extracción visual (cero añadido), integración/generación (conflicto no resuelto) y explicación/citas (atribución incorrecta). No es un error de recuperación: el campo correcto sí llegó. Sería perjudicial para un analista usar ese monto diez veces mayor sin verificación humana.

No se aprueba el sistema para decisión contractual. El 9/10 es un proxy literal, no accuracy semántica global ni tres dimensiones finales. La versión nueva añade un control posterior al fallo y debe declararse post-hoc.

## Corrección posterior, separada

[Control de consistencia 0.3](../../CONTROL_CONSISTENCIA.md). Se compara monto/modalidad de la lectura con campos inequívocos del snapshot para el mismo ID; no se sustituye el dato leído por el esperado. La [reproducción CPU](../source_guard_cpu_01/metadata.json) bloquea vis_04 y conserva las otras nueve salidas. Es reutilización de lecturas/respuestas guardadas, no nueva inferencia ni nuevo puntaje del VLM. Se conservan este ZIP y sus métricas originales.
