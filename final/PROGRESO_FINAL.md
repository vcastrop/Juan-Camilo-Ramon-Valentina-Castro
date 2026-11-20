# Avance de la entrega final — 19/11/2026

Estimación operativa: **74–78 % (~76 %)** de la entrega final integradora. No es
nota, madurez para uso real ni porcentaje de todo el curso. El aumento reconoce
ejecución y evaluación reales, no cantidad de notebooks o pruebas.

## Evidencia vigente

- [OCR23 publicado y salud lista según usuario](evidence/space_ocr23_cpu/SALUD_LISTA.md):
  cuatro modelos, índice y OCR5.5.0; fallos de carga corregidos.
  [Siete peticiones funcionales recibidas](evidence/space_ocr23_cpu/SMOKE_RECIBIDO.md),
  sin errores. Faltan salud posterior, observabilidad confirmada y acceso externo.
  Estas pruebas no son otro benchmark ni validación general de calidad.

- Comparación 02: cinco perfiles × 22 entradas, 110 respuestas conservadas.
- Juez aceptado para esta tarea/configuración tras calibración 20/20,
  confirmación 12/12 y revisión humana con límites documentados.
- Evaluación 14: 110/110 notas válidas, código y respuestas verificadas; ninguna
  nota se sustituye por acierto o por un criterio humano.
- Dominio completo: Sin RAG 3/22, M3 7/22, FP16 16/22, NF4 11/22 y sin herramienta 15/22.
- NF4 rechazada bajo umbrales anteriores: −22,73 puntos de dominio, un fallo
  crítico nuevo y dos regresiones de invarianza. Memoria −37,60 %, p50 +42,70 %.
- 90 revisiones directas (44 + 46), ocho dudas originales y la última de m3_011
  adjudicadas; veinte equivalencias exactas documentadas. No quedan filas de dominio pendientes.
- Reporte actualizado con discrepancias, modalidades separadas y límites del juez.
- Despliegue 17 completado en T4: 441 pruebas, cinco modelos/índice y siete casos;
  error OCR bloqueado, no aprobación visual general. [Diagnóstico 18 congelado](VISUAL_DESPLIEGUE_18.md).
- Visual 18 recibido: 449 pruebas y ocho casos, pero 0/5 legibles útiles; utilidad
  visual rechazada. [OCR 19](evidence/ocr19_completed/ANALISIS.md) completó 8/8 lecturas
  y 12/12 rutas diagnósticas CPU; no es calidad QA ni sustitución del scorecard.
  [Integración20](evidence/integration20_completed/ANALISIS.md) completó 22+16 casos;
  [cierre21](evidence/evaluation21_completed/ANALISIS.md) ya completo con ocho
  notas nuevas y catorce idénticas transferidas, media juez 4,4545 y dominio18/22.
  Diez revisiones visuales nuevas y doce textuales transferidas; cuatro fallos
  textuales persisten. La auditoría no regenera respuestas ni consume API.
- Presupuesto estimado/reservado USD 5,9179725 dentro de USD 7 totales autorizados;
  no factura verificada. No se necesita más gasto para este cierre.

## Estimación ponderada interna

| Hito | Peso | Avance | Pendiente principal |
|---|---:|---:|---|
| Fase 0: insumos/base | 10 % | 80 % | Inventario/roles definitivos. |
| Fase 1: producto/infraestructura | 10 % | 60 % | Integración contractual pública. |
| Fase 2: integración de desarrollo | 20 % | 75 % | Corregir/verificar fallos y servicio final. |
| Fase 3: evaluación común | 15 % | 95 % | Cierre completo reproducible; reproducción final desde limpio pendiente. |
| Fase 4: eficiencia | 15 % | 90 % | Publicación de configuración final; resultado NF4 negativo ya medido y decidido. |
| Fase 5: comparativas/ablación | 10 % | 90 % | Tablas completas; diagrama/lectura final y ensayo de presentación pendientes. |
| Fase 6: producción/observabilidad | 10 % | 25 % | Peticiones contractuales reales, salud y acceso externo. |
| Fase 7: reporte/presentación | 7 % | 50 % | Reporte con resultados completos; faltan roles, portada y diapositivas. |
| Fase 8: cierre verificable | 3 % | 0 % | Clon limpio, accesos/licencias, PR/merge y entrega. |

La tabla ponderada anterior daba ~71,75 %; el rango vigente incorpora además la
recepción visual21, corrección de portabilidad y cierre semántico OCR21; no cuenta
el despliegue público como completo. La aproximación no pretende precisión estadística. No son
pesos de la rúbrica académica ni garantía de resultados.

## Ruta inmediata — no repetir inferencia anterior

1. Conservar [scorecard completo](evidence/domain_review46/RECEPCION.md), originales
   y discrepancias. No repetir evaluaciones ni revisiones para buscar mejores notas.
2. Seguir [la preparación del servicio](DESPLIEGUE_SIGUIENTE.md): FP16 como candidato;
   no desplegar NF4. Integrar el sistema
   contractual público y verificar texto, imagen, cálculo, abstención, errores,
   salud/listo, privacidad y W&B accesible. El Space comprobado sigue siendo infraestructura.
   Las [fallas de instalación 16](evidence/deployment16_failed/ANALISIS.md) y de
   historial 17 son antecedentes resueltos. [La corrida 17 posterior completó
   inferencia real](evidence/deployment17_completed/ANALISIS.md), con un fallo OCR
   bloqueado. [Visual 18](evidence/visual18_completed/ANALISIS.md) confirmó falta
    de utilidad. OCR19 aportó extracción útil; [integración20](INTEGRACION_20.md)
   ya recogida sobre el mismo conjunto y [evaluación21](EVALUACION_21.md)
   ya cerrada por equivalencia exacta y revisión visual nueva. No repetir 17–21. ZeroGPU sigue
   pendiente. No contar estos diagnósticos como despliegue público terminado.
3. Terminar reporte, contribuciones/uso de IA y presentación.
4. Reproducción desde limpio, revisión de tablas/accesos/licencias y cierre de
   PR/merge solo autorizado; entrega y comprobante en Interactiva.

[Scorecard y auditoría](evidence/product_14/ANALISIS.md), [reporte](reporte.md),
[checklist](CHECKLIST.md). Los estados anteriores se conservaron en
[historial](HISTORIAL_PROGRESO_HASTA_EVALUACION14.md); no son instrucciones para
repetir corridas ni autorizaciones vigentes de gasto. No se declara 100 %.
