# API 07: indisponibilidad, cero notas recibidas

Auditado el 18/11/2026. Código `71912f1c5755790381a8e39c8a67801bcbf9243d`. [Integridad](audit.json): diez hashes de fuente verificados, mismo contenido fuente del notebook, seis celdas ejecutadas sin errores, resumen y hash del registro de presupuesto comprobados. Logs: 164 pruebas final + 128 M3.

El catálogo respondió con models/gemini-3.8-flash y el conteo previo permitió enviar una generación. La primera petición generateContent recibió **HTTP 503**. No hubo texto final, modelVersion de generación, tokens de uso de inferencia ni nota. raw_judgements contiene un intento de attribution_bad con score=null; no es una puntuación equivocada. Los otros ocho casos del piloto y la regresión no se ejecutaron. No hay base para juzgar calidad de este candidato.

Se mantiene la reserva d0ba4d70eda44c609b9f3da2e9b8a9ec de **USD 0,3072**. Es una estimación de exposición reservada antes de enviar, **no una factura ni prueba de cargo**. No se libera suponiendo que el 503 costó cero. El proyecto fue declarado gratuito por el titular; el programa no verifica automáticamente su facturación.

Estado stopped_api_or_format_failure, último error api_http_error/503 y una sola generación intentada, sin retry automático. W&B n7oy6os9 finalizó según logs; acceso al dashboard no verificado. Originales preservados sin editar.

Se autoriza después de revisar esta evidencia una [única recuperación explícita](../../JUEZ_API_08_REINTENTO.md), sin cambiar modelo, instrucciones, rúbrica, semilla ni umbrales. Requiere el registro y marca originales en Drive, conserva la reserva y crea otra marca exclusiva; no permite volver a seleccionar una nota, porque ninguna se recibió. Si vuelve a fallar disponibilidad, detenerse.
