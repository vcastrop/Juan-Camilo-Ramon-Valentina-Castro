# OCR 19 completado — lectura útil, no aprobación contractual

Originales conservados sin modificar:

- ZIP SHA256 `9092d91a272cd1c8de738e3cef9a0c7202ceff9e2ae6178af8338f5f314d3af7`.
- Notebook SHA256 `7aebecc5251cfb33f328282593dcd781ad2b61398d1dfda052ce4370f9d14630`.
- Código `c039a41bff4d0396c925179c38bf17c9ad7819a5`.
- Protocolo SHA256 `de78945ea0d314a0a1049cd9711b3ec50ff502abd9ac0351d8e4460969326f08`.

Los doce PNG corresponden al protocolo fijado y sus hashes verifican. Se
recalcularon los diagnósticos y los parseos de los TSV guardados: coinciden.
Notebook sin errores, nueve pruebas nuevas aprobadas en CPU y doce entradas
completadas. No se ejecutó otra vez la suite completa ni el benchmark en 19.

Tesseract 5.3.4, spa+eng, OEM1, PSM3/6, umbral80, sin reintentos/GPU/API.
Datos spa SHA256 `6f2e04d02774a18f01bed44b1111f2cd7f3ba7ac9dc4373cd3f898a40ea6b464`;
eng `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`.
Las lecturas acumularon 29,23 s en esta ejecución CPU; no comparar con el p50/p95
de otros sistemas/máquinas ni interpretar como reducción de latencia del producto.

**8/8 lecturas completas y 12/12 rutas diagnósticas esperadas.** Incluye leer
250000000 sin el cero extra, cifras con separadores y la ficha ficticia nueva.
Valor ausente quedó null; blanco, falta de ID y valores ambiguos se rechazaron.
Los ocho completos incluyen dos formatos de una misma ficha ficticia y un valor
alterado: no son ocho contratos independientes ni ocho respuestas QA correctas.

Leer 251000000 en la imagen alterada es correcto como transcripción. La prueba
19 no lo comparó con el snapshot 250000000: esa discrepancia debe bloquearse
en la integración. No hay aprobación semántica humana, generación de respuesta,
fuentes recuperadas ni juez en esta prueba. Dos segmentaciones de un mismo motor
tienen errores correlacionados; la confianza80 no significa probabilidad80%.

No reemplazar el 0/5 de utilidad integrada de Qwen18 por 8/8 OCR: miden cosas
distintas. El candidato aporta evidencia de extracción en una muestra pequeña,
sintética y post-hoc. Se justifica probar su integración separada, no publicar
ya ni adjudicarle el scorecard 16/22 histórico del perfil integrado Qwen.
