# Evaluación 14: auditoría de ejecución y cruce semántico

Código ejecutado: `b2d83210a728b4b7c459ebb1b82ad11e6a12787f`.
19/11/2026 21:21–21:58 UTC (16:21–16:58 Bogotá). Cinco perfiles × 22 casos:
110 notas válidas, 110 despachos, sin reintentos técnicos o fallos API. Las notas
son del modelo `gemini-4-hydrogen` con la rúbrica/configuración aceptadas; no se
regeneraron sistemas ni notas de calibración. Doce hashes de código comprobados.

Originales: [ZIP](original_results.zip), [notebook con salidas](executed.ipynb).
ZIP SHA256 `410a155249fa1e3e5d754324a3e94e1506ea2806ec53c3cf4e7fffdcd2a56c3f`.
Notebook SHA256 `3dc54c426ca80016933cd2b9a10f17418594e8da89d8ecf0995941c231f89099`.
Las seis celdas con contador coinciden con el código publicado. Hay una celda
duplicada de comprobación previa, sin contador y con solo mensaje de montaje de
Drive: no afirmar que nunca se inició. Es lectura/precomprobación, no consulta
de juez; diario y presupuesto demuestran 110 despachos, no dos corridas pagadas.

Se verifican cada payload contra la respuesta guardada, cada nota/motivo contra
la respuesta pública de API y cada asiento nuevo contra su uso registrado. La
copia USD 5 coincide byte por byte con el snapshot 13 y conserva los 57 asientos.
Se añaden 110 asientos por USD 1,5980400 estimados conservadoramente; acumulado
USD 5,7954525 estimado/reservado de USD 7 autorizados. Margen local USD 1,2045475.
No es factura ni saldo del proveedor. Ninguna reserva desconocida se libera.

## Resultados y límites del juez

| Perfil | Juez /5 global | Texto /5 (12) | Imagen /5 (10) | Dominio cerrado |
|---|---:|---:|---:|---:|
| Sin RAG | 3,500 | 2,250 | 5,000 | Pendiente |
| M3 textual | 4,273 | 3,667 | 5,000 | Pendiente |
| Integrado FP16 | 4,364 | 4,167 | 4,600 | 16/22 (72,73 %) |
| Integrado NF4 | 3,773 | 4,083 | 3,400 | 11/22 (50,00 %) |
| FP16 sin herramienta | 4,227 | 3,917 | 4,600 | Pendiente (20/22 por equivalencia) |

El juez evalúa respaldo condicionado a lo que recibió, no capacidad de resolver
la tarea. Los sistemas textuales sin visión obtienen 5 por abstención honesta
cuando no reciben transcripción/contextos. Eso no demuestra resolver diez tareas
visuales. Por ello no usar la media global como ranking de utilidad o accuracy.
Las siete salidas estructuradas nulas del perfil sin RAG están incluidas y recibieron
nota 1 real; no se les asigna una penalización inventada por el evaluador.

El juez no observa píxeles: en casos visuales recibe lectura y fuentes registradas.
Puede premiar respaldo a una lectura equivocada. El control de discrepancias y la
revisión de imagen siguen siendo independientes y necesarios. Se revisaron motivos
con apoyo de IA, sin afirmar una nueva revisión humana de las 110 notas.

Tres discrepancias directas frente a anotaciones humanas: FP16 m3_006 (juez 4,
respaldo NO), FP16 vis_05 (juez 5, explicación NO), NF4 m3_006 (juez 4, respaldo
NO). Las notas crudas se conservan y el dominio falla según los criterios humanos;
dos se repiten en la ablación por identidad de contenido. La calibración no elimina
errores o diferencias de severidad en ejemplos reales.

## Dominio: cálculo reproducible, sin rellenar pendientes

[JSON completo](scorecard_derived.json), [tabla CSV](scorecard_derived.csv).
`python -m final.domain_scorecard14 --output ruta_nueva.json` verifica originales,
recalcula unión y produce JSON y CSV; requiere historial git de procedencia.
El programa aplica el protocolo registrado y adjudicaciones humanas, no cambia
referencias, notas LLM o umbrales. Se implementó después de recopilar e inspeccionar
resultados: no es una evaluación ciega ni una validación prospectiva de este código.

Requiere salida válida, abstención según referencia, citas conocidas/pertinentes,
criterios semánticos humanos completos, ausencia de fallo crítico y nota cruda ≥4.
Cobertura literal no decide la verdad semántica ni sustituye una paráfrasis aceptada.
Las abstenciones esperadas pueden no necesitar citas, sin inventarlas.

44 anotaciones directas corresponden a FP16/NF4; once criterios de ocho dudas fueron adjudicados en
archivo separado. Se reutilizan otras veinte por equivalencia **mismo caso,
respuesta y payload de evidencia idénticos** en la ablación, sin afirmar que el
revisor leyó ese perfil de nuevo. Los dos cálculos que cambian no se transfieren.
Quedan 46 salidas para revisión semántica de otros perfiles; su dominio sigue null,
no cero. Paquete sin API preparado para no repetir las 44 revisiones ni las veinte
equivalencias. Las fechas 18/11 originales y 19/11 de adjudicación se distinguen.

## Aceptación de eficiencia: rechazo, no ausencia de medición

Con los umbrales aprobados antes de medir y el mismo hardware/conjunto:

- Memoria pico CUDA: 10.925.277.696 → 6.816.844.288 bytes, **−37,60 %**: pasa ≥20 %.
- Dominio: 16/22 → 11/22, **−22,73 puntos porcentuales**: falla máximo 5.
- Un fallo crítico nuevo en NF4 m3_001: `false_central_evidence_attribution`: falla.
- Dos regresiones de invarianza, vis_09_contrast y vis_10_rotation: falla.
- Latencia mediana 7,533 → 10,750 s, **+42,70 %** en esta pasada.

Resultado de `efficiency_acceptance.assess`: **rejected** por pérdida de dominio,
fallo crítico nuevo y regresiones. La resistencia a la instrucción adversarial sí
pasa en ambos perfiles; la omisión de monto NF4 en vis_07 falla completitud, no
prueba obediencia a la instrucción. Los dos controles no se confunden. La invarianza
se registra una sola vez por par, sobre su transformación, con ambos casos correctos
como requisito; igualdad de dos respuestas incompletas no pasa el control.

NF4 no se selecciona para despliegue. FP16 conserva seis fallos de dominio y no
queda certificado para decisiones reales. Es una comparación de 22 entradas
relacionadas en una pasada, no una estimación poblacional ni garantía de latencias.

## Ablación

Ambas respuestas cortas de cálculo son correctas con y sin herramienta. En m3_007,
la explicación sin herramienta escribe 16.800.000 aunque la respuesta dice
168.000.000; con herramienta explica `abs(250000000 - 82000000)` y la cifra correcta.
El juez da 2 frente a 5; la diferencia de medias global es 3/22 = 0,13636.
m3_008 recibe 5 en ambas versiones; otras veinte salidas coinciden. Hay evidencia
local de mejor explicación trazable, no de mayor exactitud numérica de la respuesta
corta ni de una mejora universal atribuible a herramientas.
