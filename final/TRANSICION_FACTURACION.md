# Transición de facturación del juez — 19/11/2026

Estado: **preparación sin consultas; no habilitado para ejecutar en modo pago**.
El usuario informa que activó la facturación. No se han verificado importe real,
saldo, modalidad de pago ni límite del proveedor. El techo autorizado sigue siendo
USD 5 totales, no USD 5 adicionales.

Actualización posterior del 19/11/2026: el usuario aportó las capturas de Projects,
Billing y Spend: mismo proyecto indicado, nivel 1, prepago COP 60.000, recarga
automática desactivada. El período 23/10–19/11 incluye los intentos y muestra
COP 0,00 con advertencia de demora de horas o más de 24 horas. No hay límite de
proyecto configurado visible. Esto documenta estado mostrado, **no factura final
ni verificación de la vinculación de la clave con el proyecto por la API**.
No se publican las capturas de cuenta ni sus identificadores de facturación.

Preparado ahora [Juez 12](JUEZ_12_PAGO.md): modo pago explícito, ocho asientos
preservados, marcador nuevo, ninguna repetición automática de transporte y techo
acumulado USD 5. Código probado con respuestas simuladas, no servicio validado.
No se han hecho consultas pagadas en la preparación. Las condiciones anteriores
de gasto real se conservan como pendientes de conciliación, no se marcan verificadas.

## Evidencia recibida

Originales preservados localmente, sin modificar:
[primera corrida](evidence/hydrogen_11/original_results.zip),
[notebook ejecutado](evidence/hydrogen_11/executed.ipynb),
[reejecución](evidence/hydrogen_11_billing_rerun/original_results.zip) y
[su notebook](evidence/hydrogen_11_billing_rerun/executed.ipynb).
Trabajo exclusivo de la rama de entrega final; no modifica main o el Space.

- Primera recuperación 11: dos solicitudes de generación fallidas con HTTP 503,
  ninguna calificación nueva. El snapshot conserva ocho asientos, incluyendo
  todos los seis anteriores, por USD 3,6994725 estimados o reservados.
- Segunda recuperación 11, tras la activación comunicada: bloqueada por
  `same_drive_accounting_required_do_not_reset` antes de consultar la API.
  No demuestra si la facturación resolvió el 503. Conserva una nota histórica;
  no es una nota nueva ni validación del juez.
- Su metadata declara proyecto gratuito porque el notebook pedía una confirmación
  manual. Esa declaración no verifica el estado de Google y es incompatible con
  la activación comunicada. Se conserva el original; no se corrige retrospectivamente.

El margen local no reservado es USD 1,3005275. **No es saldo de Google ni dinero
confirmado disponible**. No se liberan reservas de errores por suponer coste cero.
El validador `paid_transition_preflight.py` solo lee archivos: no accede a claves,
no hace peticiones, no cambia Drive y siempre mantiene deshabilitada la ejecución.

## Información necesaria del titular

1. Abrir [Projects](https://aistudio.google.com/projects) e identificar el mismo
   proyecto de la clave de Colab. Mostrar su nivel y estado, ocultando datos de pago.
2. Abrir [Spend](https://aistudio.google.com/spend), seleccionar ese proyecto y el
   período que incluya todos los intentos (18–19/11/2026). Mostrar importe, moneda
   y período. Si está vacío o dice pendiente, conservar ese estado sin asumir cero.
3. En [Billing](https://aistudio.google.com/billing), indicar si es prepago o pospago
   y si hay recarga automática. No compartir clave API, tarjeta ni dirección.
4. No ejecutar de nuevo Juez 11 ni eliminar `ContractRisk_final_budget` o sus
   marcadores. No hacer recargas adicionales para esta comprobación.

## Condiciones de la continuación

Antes de preparar un notebook ejecutable en pago: revisar la información anterior,
verificar tarifa y vigencia, validar el snapshot actual de Drive frente al último
de ocho asientos y conservar los marcadores y la nota válida. La continuación
requiere modo pago explícito, marcador nuevo exclusivo y parada ante fallo; no se
autoriza un bucle de reintentos. No se cambian umbrales ni notas para aprobar.
El despliegue, reporte y revisión del producto siguen pendientes independientemente
de la disponibilidad del juez; este paso no incrementa por sí solo su calidad.

## Referencias oficiales consultadas

Consulta del 19/11/2026: [facturación](https://aistudio.google.com/docs/billing)
y [tarifas](https://aistudio.google.com/docs/pricing). Google documenta límites de
gasto de proyecto en Spend, pero advierte de retrasos y posibles excesos; no son
garantía instantánea de USD 5. Las alertas y el registro local tampoco equivalen
a una factura ni a una garantía del proveedor.
