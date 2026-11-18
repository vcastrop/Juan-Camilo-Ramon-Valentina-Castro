# Hydrogen 10: reintento ejecutado, sin nuevas notas

Auditoría del 18/11/2026. [Comprobaciones y hashes](audit.json). Originales ZIP/notebook preservados byte a byte; 14 archivos fuente corresponden al commit `4c404c9d2bcca3fae05225a2aa74a1d0462441c1`. Las seis celdas de código se ejecutaron sin salidas de excepción. Los logs registran 193 pruebas final y 128 M3 aprobadas.

## Qué ocurrió

1. Se reutilizó `attribution_bad` con nota 2 y el objeto de juicio completo idéntico al de 09. No se regeneró.
2. Se solicitó `attribution_good`: HTTP 503, estado del proveedor `UNAVAILABLE`.
3. Se esperaron 30,353 segundos y se hizo un reintento técnico con el mismo contenido y semilla. Su hash coincide con la petición pendiente de 09.
4. El segundo intento terminó como `api_transport_or_json_error`, sin estado HTTP registrado y sin nota. El cliente agrupa transporte y decodificación JSON: no permite concluir que fue otro 503 ni afirmar que fue específicamente un timeout.
5. Se detuvo según política: solo HTTP 503 permite reintento; no se reintenta automáticamente un error de transporte/JSON. Se usó uno de los dos reintentos máximos globales. No se activó ningún ciclo infinito ni se corrigieron puntuaciones.

El marcador de continuación impide volver a lanzar 10 accidentalmente. **No repetir el notebook ni borrar el marcador o el registro de Drive.** Primero hace falta revisar el diagnóstico/estrategia de acceso, no seguir enviando peticiones sin límites.

## Cómo leer el resultado

- Dos filas no son dos notas: una nota válida histórica reutilizada y un juicio nuevo sin respuesta.
- Cero notas nuevas. Piloto incompleto: 1/9 con nota, uno sin respuesta y siete sin ejecutar. No se ejecutaron la regresión completa ni la confirmación separada.
- `failed_ids=[]` no significa aprobado: `invalid_ids=[attribution_good]` y `pilot_passed=false`.
- `actual_model_version` se hereda de la respuesta válida de 09. No prueba que en 10 haya llegado una nueva respuesta de ese modelo.
- No hubo excepciones visibles en las celdas porque el programa manejó el fallo y guardó evidencia; esto no equivale a completar la evaluación.
- W&B terminó según logs/metadata; el acceso externo y el contenido del dashboard no se verificaron aquí.
- El juez sigue **sin validar**, pero esta corrida tampoco demuestra mal juicio: no llegó una calificación nueva que permita evaluarlo.

## Presupuesto y privacidad

Las reservas anteriores permanecen idénticas. Dos nuevos intentos agregaron USD 1,2288 en reservas conservadoras. Total acumulado estimado/reservado: **USD 2,4706725**, bajo el techo local USD 5. No son cargos ni factura confirmados; el proyecto fue confirmado gratuito por el titular. No se libera una reserva desconocida ni se reinicia el ledger para repetir.

Escaneo de patrones de credenciales en notebook y contenido del ZIP: sin coincidencias detectadas, no garantía absoluta de ausencia de cualquier secreto. No se guardaron mensajes completos del proveedor ni texto de pensamiento.

## Próximo paso

Adelantar la [revisión humana de 12 casos separados](../../REVISION_CONFIRMACION_PASOS.md), sin inferencia ni costo. Conservar el estado técnico bloqueado del juez; no marcarlo aprobado ni usarlo para un scorecard definitivo. Una futura reanudación debe preservar esta evidencia y la única nota válida, diagnosticar fallos de transporte de forma sanitizada y respetar el presupuesto acumulado. No preparar una nueva corrida ciega o activar facturación por este resultado.
