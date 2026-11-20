# Integración20 completada: evidencia nueva y equivalencias verificadas

Originales preservados sin modificar:

- ZIP SHA256 `af18c90271ec3561057644f672f9619d064ce6a135dd6bb6c21cc68a2b17db21`.
- Notebook SHA256 `567a1d43a95a02c4f46bf9b2b2d393503488ce34dad44dbfa681bb303b4323bb`.
- Código `1b0e080daa21b9d3298a58f6217c13c55eb44e97`.

Sin errores de celda, 339 pruebas final + 128 M3 (467). Terminó 22 casos comunes
y 16 comprobaciones separadas. Se verificaron huellas de fuentes contra commit,
manifiestos y diagnósticos recalculados. Ninguna llamada al juez en esta corrida.
Cuatro modelos neurales y OCR5.3.4, no Qwen2-VL. T4/Torch2.14.1+cu130.

Los diez casos visuales comunes pasan los chequeos automáticos: ocho respuestas
de modalidad/valor y dos abstenciones esperadas. Las dos transformaciones
conservan los hechos; la nota adversarial no se ejecuta como instrucción.
Dieciséis comprobaciones tienen la guarda esperada: cinco QA visuales, nueve
bloqueos (incluido importe alterado/ID/ambigüedad/auditoría) y M1 texto/imagen.
Confianza de M1 no calibrada: ejecución no demuestra acierto poblacional.

Cobertura literal media 0,7121212 y 14/22 chequeos automáticos pasan (4 texto y
10 imagen). **No son exactitud, dominio ni nota del juez.** Paráfrasis correctas
pueden fallar el chequeo; también hay errores semánticos reales. m3_009 sigue
diciendo que 2019 es posterior a 2024; no se corrige la respuesta ni se oculta.

Comparando paquetes exactos del juez con FP16 histórico: 14 idénticos (12 texto,
blanco y valor ausente), ocho cambiados. Se transfieren las 14 notas sin cambiar
puntajes/motivos. Se transfieren solo doce revisiones humanas textuales; se pide
nueva revisión de las diez imágenes porque el lector cambió. No afirmar 14
revisiones humanas nuevas ni omitir los cuatro fallos textuales históricos.

La etapa21 evaluará las ocho salidas guardadas cambiadas, mismo modelo, rúbrica,
semillas y control de verbosidad. No regenera sistemas ni usa gold con el juez.
Notas nuevas y revisión visual humana todavía pendientes; no publicar media
parcial o dominio. No inferir mejora de eficiencia por retirar VLM: no se midió
un antes/después controlado de este cambio. Space, observabilidad pública,
reporte final y presentación siguen pendientes.
