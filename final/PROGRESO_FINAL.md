# Avance de la entrega final — 19/11/2026

Estimación operativa: **70–75 % (~72 %)** de la entrega final integradora. No es
nota, madurez para uso real ni porcentaje de todo el curso. El aumento reconoce
ejecución y evaluación reales, no cantidad de notebooks o pruebas.

## Evidencia vigente

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
- Presupuesto estimado/reservado USD 5,7954525 dentro de USD 7 totales autorizados;
  no factura verificada. Este recálculo no consume API.

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

Suma interna ~71,75 %, expresada como rango para no fingir precisión. No son
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
   bloqueado. Seguir con [diagnóstico visual 18](VISUAL_DESPLIEGUE_18.md), una
   tanda acotada y post-hoc; no repetir 17 ni el benchmark. Verificación en
   ZeroGPU sigue pendiente. No contar esta recepción como despliegue público terminado.
3. Terminar reporte, contribuciones/uso de IA y presentación.
4. Reproducción desde limpio, revisión de tablas/accesos/licencias y cierre de
   PR/merge solo autorizado; entrega y comprobante en Interactiva.

[Scorecard y auditoría](evidence/product_14/ANALISIS.md), [reporte](reporte.md),
[checklist](CHECKLIST.md). Los estados anteriores se conservaron en
[historial](HISTORIAL_PROGRESO_HASTA_EVALUACION14.md); no son instrucciones para
repetir corridas ni autorizaciones vigentes de gasto. No se declara 100 %.
