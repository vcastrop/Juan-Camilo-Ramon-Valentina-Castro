# Evaluación 14 — respuestas reales guardadas, techo USD 7 total

El usuario autorizó expresamente el 19/11/2026 elevar el límite de USD 5 a **USD 7
TOTALES**. No son USD 7 adicionales, no se ha autorizado una recarga y no se
libera ninguna reserva desconocida. Esto reemplaza solo el techo operativo para
esta nueva ejecución; no reescribe presupuestos o metadatas históricas.

## Qué ejecuta

`ContractRisk_Final_Evaluacion_14_Colab.ipynb` usa CPU y los secretos existentes
GEMINI_API_KEY y WANDB_API_KEY. Evalúa las 110 salidas de Comparación 02: cinco
perfiles, mismos 22 casos. No ejecuta de nuevo el sistema, visión, recuperación,
herramientas, calibración ni confirmación. No manda gold ni etiquetas de acierto
o nombres de perfil al juez. Mantiene modelo, rúbrica, sesgo controlado, semillas
por caso y configuración de generación validados. Una nota válida baja se guarda
y no se repite. Incluye las siete salidas con `output=None`: el juez recibe que
no hubo salida estructurada utilizable, no una respuesta inventada; el texto crudo
de intentos fallidos sigue en la evidencia original, no sustituye el contrato de salida.

Las notas no son exactitud ni completan por sí solas el dominio. El resumen deja
dominio pendiente y solo publica media cuando el perfil tiene sus 22 notas válidas.
Una corrida parcial se etiqueta parcial; no se presenta como cinco perfiles completos.

## Protección del presupuesto

Primero exige la misma cuenta de Drive, el registro exacto de 57 asientos por
USD 4,1974125 estimados/reservados, siete marcadores previos y el cierre humano.
La celda previa solo lee y comprueba; no cambia presupuesto ni hace consultas.
La ejecución crea marcador exclusivo `product_judge_14.started.json` y después:

1. Conserva el registro anterior byte por byte en `api_budget_ledger_before_usd7.json`.
2. Registra la autorización y la huella de esa copia en `api_budget_authorization_usd7.json`.
3. Cambia únicamente `limit_usd` a `7.00`, sin alterar los 57 asientos.
4. Antes de cada despacho reserva USD 0,6144; ajusta solo ese asiento con uso
   devuelto por la API, estimado conservadoramente. Fallos sin uso conservan reserva.

Margen inicial USD 2,8025875, no saldo de Google. El cliente USD 7 verifica la
autorización y todos los asientos históricos en cada transacción. Los clientes
históricos USD 5 no pueden consumir silenciosamente el nuevo registro. Un bloqueo,
archivo faltante, copia alterada o límite insuficiente detiene la ejecución.
No hay reinicialización ni recuperación automática de candados o ejecuciones.

Sin reintentos de 503/red/timeout; solo se conserva la reparación de formato
original, una como máximo por juicio. No se usa un bucle para conseguir notas
favorables. Un cargo que supere la reserva bloquea futuras peticiones y se reporta;
el registro local no es factura ni garantía de un límite impuesto por Google.
No cubre consumo ajeno: confirmar que no hay otro uso paralelo del proyecto.

## Pasos en Colab

1. Abrir el notebook y usar CPU, sin GPU.
2. Habilitar los dos secretos existentes para este notebook y ejecutar en orden.
3. Montar la misma cuenta de Drive. Confirmar `EVALUAR_110_MAXIMO_TOTAL_7_USD`
   solo con prepago activo, recarga automática apagada y ningún uso paralelo de API.
4. Mantener la ejecución abierta. Las filas y el diario se escriben progresivamente
   en `MyDrive/ContractRisk_final_product14_results`, no solo en el disco temporal.
5. Al terminar o detenerse, ejecutar inspección y descarga; devolver el ZIP
   `contractrisk_final_evaluacion14_resultados.zip` y notebook con sus salidas.

No borrar ninguna carpeta, marcador, copia o registro para repetir. Si falla,
no reejecutar: conservar parciales para diseñar una continuación que no pierda
notas. No comprar más créditos ni cambiar claves por un error del proveedor.

## Tarifas y alcance

Tarifas Standard consultadas el 19/11/2026: entrada USD 1,50/M y salida incluido
razonamiento USD 7,50/M. Sin grounding ni herramientas facturables de la API.
[Fuente oficial](https://aistudio.google.com/docs/pricing#gemini-4-hydrogen).
Después de 20/11/2026 UTC requiere nueva revisión de precios antes de ejecutar.
El cambio de presupuesto no modifica el payload de generación ni baja el límite
de salida. USD 7 es un máximo, no gasto previsto ni garantía de completar 110.

Esta preparación no hace consultas pagadas y no modifica main o el Space.
