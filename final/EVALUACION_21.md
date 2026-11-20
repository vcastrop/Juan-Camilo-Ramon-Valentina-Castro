# Cierre de calidad del perfil OCR20

**CERRADO:** [resultado auditado](evidence/evaluation21_completed/ANALISIS.md):
22 notas, media 4,4545 y dominio 18/22 tras revisión humana. Se conserva el
fallo de preparación y el cierre posterior, sin reescribir originales.
**No volver a ejecutar la API ni las instrucciones históricas de abajo.**
El pendiente siguiente es despliegue/observabilidad públicos, no más evaluación.

**Actualización:** revisión humana de diez imágenes recibida y validada. La
primera ejecución21 se detuvo en preparación por CRLF/LF, antes de API. El
chequeo corregido conserva el mismo contenido y plan. Actualizar el checkout y
repetir preparación antes de ejecutar API por primera vez; no borrar marcadores
Drive. [Diagnóstico](evidence/evaluation21_setup_failed/ANALISIS.md).

La [corrida20](evidence/integration20_completed/ANALISIS.md) quedó preservada.
El plan reproducible `evaluation21.py` verifica originales, fuentes y conjunto
común antes de transferir valoraciones. No cambian umbrales ni criterios.

## Dos trabajos separados, sin regenerar respuestas

1. **Juez:** 14 notas por equivalencia exacta de su paquete; ocho notas nuevas.
   Incluye conservar el 2 de m3_009, no promoverlo. Misma rúbrica y configuración
   calibradas/confirmadas. El juez no recibe referencias, perfil ni comparación
   de etiquetas. No ve píxeles: la revisión humana sigue siendo necesaria.
2. **Humano:** doce anotaciones textuales previas transferidas con nombre/fecha
   originales, sin atribuir nueva revisión; diez imágenes requieren revisión
   nueva. El paquete no muestra notas del juez para no condicionar decisiones.

## Revisión visual: instrucciones

Descomprimir el ZIP `contractrisk_revision_visual21.zip` y abrir `index.html`.
Cada sección muestra la imagen original, pregunta, referencia, salida OCR,
respuesta, explicación y fuentes. Editar `REVISION_VISUAL_21.md`:

- Escribir revisor/a y fecha reales.
- Completar los cinco criterios con SI/NO/DUDOSO; Citas puede ser NO_APLICA
  solo en abstención esperada. Fallos críticos: NINGUNO/DUDOSO o tipo indicado.
- Anotar una razón breve por caso. No modificar respuestas, referencias o imágenes.
- Revisar también blanco, dato ausente e instrucción adversarial; abstenerse no
  demuestra por sí solo haber detectado la causa correcta.
- Devolver únicamente el Markdown editado. La IA no firma estos criterios.

## Ocho evaluaciones API en CPU, con la cuenta existente

Notebook `ContractRisk_Final_Evaluacion_21_Colab.ipynb`, hardware CPU/Ninguno.
Usa GEMINI_API_KEY existente y el mismo Drive. No necesita T4, W&B ni claves nuevas.
Se monta Drive y exige confirmación explícita de mismo proyecto de prepago,
uso exclusivo durante la corrida y autorización **USD7 TOTALES**.

No migrar ni reiniciar presupuesto: exige los 167 asientos del cierre14 por
USD5,7954525 estimados/reservados. Margen local USD1,2045475, no factura/saldo.
Se reserva USD0,6144 por despacho, se liquida solo ese asiento con uso verificado
y se detiene si no alcanza el margen. No se liberan reservas ambiguas.
Ocho casos no garantizan ocho llamadas: el protocolo conserva una reparación de
formato, pero no reintenta 503/transporte ni una nota baja. No garantiza terminar.

Precios Standard siguen USD1,50/M entrada y USD7,50/M salida incluido pensamiento,
verificados en la [fuente oficial](https://aistudio.google.com/docs/pricing#gemini-4-hydrogen).
Se conserva el vencimiento de comprobación del cliente (20/11/2026 UTC); después
se detiene antes de gastar. El guardia local no es límite global del proveedor:
no consumir la API en paralelo y mantener recarga automática desactivada.

Los resultados se guardan en `MyDrive/ContractRisk_final_evaluation21_results`;
el marcador persistente impide repetir. No borrar resultados/marcadores si falla.
Devolver ZIP y notebook con salidas, usando la última celda incluso si se detuvo.
No se harán llamadas pagadas desde este entorno local.

Comprobación local de preparación: 347 pruebas de final y 128 de M3 (475 en
total) pasaron. Incluye ocho pruebas nuevas con transporte simulado, sin gasto
API, igualdad del plan congelado, compilación de las celdas y diez imágenes
embebidas en el paquete humano. No equivale a haber ejecutado la etapa21 pagada.

## Después

Auditar motivos/notas, recibir revisión humana y recalcular las 22 filas con
las reglas originales. Hasta entonces media completa y dominio quedan pendientes,
no cero ni aprobados. La siguiente etapa es desplegar y verificar la versión OCR
en ZeroGPU y W&B; estas tareas no modifican main ni el Space.
