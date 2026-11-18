# Hydrogen 09: una nota válida y una interrupción 503

Auditoría del 18/11/2026. [Comprobaciones](audit.json). Originales preservados byte a byte.

- Código ejecutado: `ece58275c2a19abfb6bbd2fe4b507731232e9083`.
- ZIP SHA256: `501f2ab9a2be78f599ff8b5468bc94597fb00de2d8b0621d89b7a16817a51c4f`.
- Notebook SHA256: `d021371892d61c3656ae00b366e2e49f8ce005cc383748c35ccc87235d70749e`.
- Seis celdas de código ejecutadas sin salidas de error; 182 pruebas final y 128 M3 aprobadas según logs. Eso no valida la calidad del juez.
- `attribution_bad`: nota cruda 2, respuesta completa STOP de `gemini-4-hydrogen`. La razón reconoce que el monto es correcto pero su atribución al campo de objeto es falsa. Coincide con el ancla en este único caso.
- `attribution_good`: HTTP 503 sin nota. No es una mala calificación ni una falla de criterio. Siete anclas del piloto no se ejecutaron; no hay regresión completa ni confirmación.
- Tokens informados en la respuesta válida: 910 de entrada, 69 visibles, 764 de pensamiento, 1743 totales. No se conserva texto de pensamiento.
- Estimación conservadora de esa respuesta: USD 0,0130725, no factura. Registro acumulado estimado/reservado: USD 1,2418725, incluyendo reservas previas y el intento 503 sin costo verificado. No se liberan ni reinician reservas.

La generación válida demuestra que la clave permitió inferencia en esa petición. No permite identificar por sí sola la causa interna del siguiente 503 ni garantizar disponibilidad futura. El cliente original se detenía al primer error, sin espera/reintento de transporte.

[Continuación 10](../../JUEZ_HYDROGEN_10_CONTINUACION.md): conserva la nota 2 y su justificación exactas; solo reanuda juicios sin nota. No se reemplaza esta evidencia ni se selecciona entre calificaciones. El juez sigue sin validar para el scorecard final.
