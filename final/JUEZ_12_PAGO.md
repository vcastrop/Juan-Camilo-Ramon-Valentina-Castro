# Juez 12 — continuación de pago limitada

No repetir Juez 11. Abrir `ContractRisk_Final_Juez_12_Pago_Colab.ipynb` en Colab
con entorno **CPU**. Habilitar acceso a los secretos existentes `GEMINI_API_KEY`
y `WANDB_API_KEY`; no compartir ni cambiar sus valores para esta prueba.

Ejecutar celdas en orden. Al montar Drive, usar la misma cuenta y carpeta
`MyDrive/ContractRisk_final_budget`. No borrar ni editar el registro ni los cinco
marcadores anteriores. Confirmar `PAGO_MAXIMO_5_USD` únicamente si se mantiene
el proyecto de prepago, recarga automática desactivada y ningún otro uso paralelo
de la API de este proyecto. Si existe otro consumo, detenerse para conciliarlo.

La comprobación inicial valida los ocho asientos de la primera corrida 11,
por USD 3,6994725 estimados/reservados. **No los borra por ver COP 0 en Google**.
El margen local inicial es USD 1,3005275 y la reserva conservadora por petición
es USD 0,6144; tras una respuesta con uso verificable se actualiza solo ese asiento.
Si falla, conserva la reserva. El límite es USD 5 TOTAL desde el inicio, no una
autorización adicional ni el saldo recargado de COP 60.000.

El cliente usa la misma configuración de generación y conserva la única nota
válida de `attribution_bad`. Reanuda `attribution_good`. Un error HTTP/red/timeout
no se reintenta. Una nota válida incorrecta se conserva y detiene el piloto;
no se pide otra para obtener aprobación. El protocolo original permite una
reparación de formato inválido, sin exceder el presupuesto. Si el piloto pasa,
continúa la regresión sintética; no evalúa aún el conjunto final ni la confirmación.

Al terminar o detenerse, ejecutar las celdas de inspección y descarga. Conservar
el ZIP `contractrisk_final_juez12_pago_resultados.zip` y descargar el notebook
con salidas desde Archivo > Descargar > .ipynb. No repetir si falla, tampoco
si el marcador exclusivo impide reejecutarlo. Entregar ambos para auditoría.

Las pruebas locales son simuladas y no prueban que Google funcione, que el
modelo juzgue bien o que el cargo final sea cero. No se promete que activar
facturación corrija el 503. El panel de Google tiene retrasos y su límite
experimental puede presentar excedentes; nuestro registro local no es factura
ni protección para usos ajenos a este programa.

Tarifas Standard consultadas 19/11/2026: entrada USD 1,50/M y salida, incluido
razonamiento, USD 7,50/M. Sin grounding ni herramientas facturables externas.
El programa exige revisión de precio después de 20/11/2026 UTC.
[Tarifas oficiales](https://aistudio.google.com/docs/pricing#gemini-4-hydrogen),
[límites y demoras](https://aistudio.google.com/docs/billing#project-spend-caps).
