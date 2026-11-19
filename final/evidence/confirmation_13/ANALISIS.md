# Recepción y auditoría de confirmación 13 — 19/11/2026

Originales: [ZIP](original_results.zip) y [notebook ejecutado](executed.ipynb).
Código de ejecución: `089caac1b23fc32cf497125aebe76cbe21a36fa4`.
Horario 20:04–20:07 UTC. Seis celdas con salidas, sin errores, mismo código
del notebook publicado. Nueve hashes de código coinciden con el commit.

- ZIP SHA256 `e07af300b1395a2df624b47184168fd3fa4eb5d01e9e059eb21ab38da3b242f1`.
- Notebook SHA256 `b92d5fc4ce68f0812a168e1fb9dcbea474f91f1b453b418ff625ced8eeb3473e`.
- Recalculado con reglas previas: 12/12 válidos y dentro de rango, cero respuestas
  malas aceptadas con 4–5. Doce peticiones, sin reintentos ni errores API.
- Puntajes: seis buenos con 5; malos de campo, cifra, conflicto y auditoría con 1;
  explicación vacía y cita al fragmento erróneo con 2. Motivos públicos idénticos
  a las filas guardadas. No se repitieron las 38 notas de calibración.
- El prompt no recibe rangos esperados ni etiquetas good/bad del evaluador.
- Los 45 asientos anteriores están intactos. Doce nuevos: USD 0,1173300 de
  estimación conservadora a partir de 15.644 tokens totales devueltos por la API.
- Acumulado estimado/reservado USD 4,1974125; margen local USD 0,8025875. No
  es factura de Google. Se conserva cada reserva anterior de coste desconocido.
- Logs: 249 pruebas final y 128 M3 aprobadas. W&B declara cierre según logs,
  no verificación de acceso externo.

Revisión técnica con apoyo de IA: los doce motivos son específicos y coherentes
con sus fuentes, sin inconsistencias materiales observadas. No equivale a firma
humana ni aprobación automática del juez. La revisión humana de las justificaciones
nuevas continúa pendiente; la revisión previa aprobaba los ejemplos, no estas notas.
La metadata original permanece `judge_validated_for_final=false` y no se reescribe.

Siguiente paso sin coste API: paquete de doce motivos para revisión humana y ocho
dudas anteriores de dominio, manteniendo todas las decisiones anteriores intactas.
Incluye anexo de los 38 motivos de calibración y un cierre humano separado:
la auditoría técnica previa de IA no se presenta como firma humana.
`final/confirmation13_receipt.py` verifica la recepción sin realizar llamadas.

## Plan de presupuesto, no autorización adicional

Cada despacho requiere reservar USD 0,6144. Quedan USD 0,1881875 antes de tocar
el margen necesario para esa reserva. Los 49 juicios nuevos de las corridas 12–13
sumaron USD 0,49794 estimados, media USD 0,010162 por juicio. Una extrapolación
meramente ilustrativa a 110 respuestas sería USD 1,117824 adicionales, mayor que
el margen actual; además no resolvería la reserva exigida antes de cada despacho.
Las preguntas del producto tienen evidencia y consumos distintos: no es un precio
garantizado ni una previsión fiable por caso.

No iniciar la evaluación completa como si el presupuesto estuviera resuelto.
No escoger solo respuestas favorables ni presentar una muestra como 110/110.
No reducir silenciosamente el límite de salida del juez calibrado ni liberar las
reservas de 503 por ver cero en un panel demorado. Antes del siguiente despacho:
cerrar revisión humana y decidir cómo conciliar gasto realmente verificable o,
si es necesario, solicitar autorización explícita para otro techo total. Por
ahora se mantiene USD 5 y no se prepara una nueva ejecución pagada.
