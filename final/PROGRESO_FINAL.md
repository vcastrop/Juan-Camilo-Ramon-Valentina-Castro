# Avance de la entrega final — 18/11/2026

Estimación operativa: **55–60 % (punto de referencia ~57 %)** de la entrega final integradora. No es nota, madurez para uso real ni porcentaje del curso completo. M1–M3 sirven de base, pero no sustituyen evaluación común, eficiencia, despliegue y documentos finales.

## Cómo se estima

Se ponderan hitos del checklist por esfuerzo/resultado, reconociendo avance parcial y separando código preparado de ejecución comprobada. Estos pesos son una herramienta interna de seguimiento, **no los puntos de la rúbrica académica**. Contar todas las casillas por igual sería engañoso: algunas preparatorias son pequeñas y una sola comparación o despliegue puede requerir mucho trabajo.

| Hito del checklist | Peso de seguimiento | Avance estimado | Evidencia o pendiente principal |
|---|---:|---:|---|
| Fase 0: insumos/base | 10 % | 80 % | Guía, rama, materiales disponibles, corpus/modelos y cuentas; inventario completo y responsabilidades pendientes. |
| Fase 1: producto e infraestructura | 10 % | 60 % | Modos/interfaz en código, Space inicial y GPU; servicio contractual público todavía no integrado. |
| Fase 2: integración de desarrollo | 20 % | 75 % | Texto/herramienta/M1 y visión probados en T4; control de conflictos observado en Comparación 02; seguridad/calidad y servicio final pendientes. |
| Fase 3: evaluación común | 15 % | 60 % | 110 registros auditados, 22 casos por perfil. Juez, revisión semántica y dominio definitivos pendientes. |
| Fase 4: eficiencia | 15 % | 60 % | Antes/después real en T4: 37,6 % menos memoria y 42,7 % más latencia mediana con NF4. Calidad/controles no aprobados; NF4 no aceptado para despliegue. |
| Fase 5: comparativas/ablación/análisis | 10 % | 60 % | Cinco perfiles y ablación medidos; siete observaciones de fallos documentadas. Falta cierre semántico y tabla definitiva con juez/dominio. |
| Fase 6: producción/observabilidad | 10 % | 25 % | Space de infraestructura y W&B de pruebas; faltan consultas contractuales reales desde despliegue. |
| Fase 7: reporte/presentación | 7 % | 25 % | Borrador integrador con resultados reales, límites y ética/IA. Faltan versión definitiva, roles confirmados, portada y diapositivas. |
| Fase 8: cierre verificable | 3 % | 0 % | Pendientes clon limpio, revisión integral, PR/merge autorizado y entrega. |

Suma ponderada: ~57,25 %, redondeada a rango 55–60 % para no atribuir precisión falsa a estimaciones de esfuerzo. Sube por la comparación real y el análisis documentado, no por número de pruebas. No significa calidad aprobada ni proximidad equivalente a producción.

## Avances comprobados hasta aquí

- Base M1–M3 preservada; trabajo nuevo en rama `Entrega/contractrisk-final`, sin cambiar main ni reemplazar Space por candidatos no verificados.
- Integración de desarrollo con datos/modelos reales, lecturas visuales nuevas en T4 y trazas de herramientas.
- Dos modelos simultáneos en T4, latencia/memoria de visual 03 y cierre W&B según logs; acceso externo y producción siguen pendientes.
- Referencias visuales revisadas por el usuario, controles de ausencia/vacío/instrucción rotulada e invarianza básica medidos.
- Error monetario de OCR y propagación documentado; mitigación de conflicto verificada por reproducción CPU sin reescribir la corrida original.
- Umbrales de eficiencia aprobados antes de comparar; 22 entradas comunes ensambladas, anclas sintéticas y rúbrica preparadas. Revisión humana de anclas cerrada con archivo + confirmación posterior.
- Calibración Qwen 7B NF4 ejecutada: carga técnica comprobada, juicio rechazado por el filtro. No se aprueba calidad por 38 JSON válidos. Segundo candidato de otra familia preparado y confirmación nueva no ejecutada.
- Mistral corregido ejecutado: 38 entradas nativas, 13/20 en rango frente a 11/20 anteriores, siete malos con nota alta y diferencia de verbosidad máxima 3. Rechazado; originales intactos.
- Nuevo protocolo por criterios y Qwen3-8B con razonamiento preparado: piloto de siete, parada temprana y misma regresión numérica si pasa. Tokenizer real 38/38 comprobado sin pesos; inferencia pendiente.
- 112 pruebas final CPU y 128 M3 aprobadas. No prueban calidad del candidato nuevo ni eficiencia del generador.

## Ruta inmediata

Actualización de revisión: se recibió [el dictamen de 44 respuestas](evidence/human_response_review_01/RECEPCION.md), con ocho dudas abiertas. NF4 queda vetado para despliegue por fallos confirmados; la evaluación numérica total continúa pendiente. [Recuperación 11 del juez](JUEZ_11_RECUPERACION.md) lista para CPU, sin inferencia nueva local ni gastos iniciados; es el siguiente ensayo técnico acotado, no una repetición para cambiar notas. Verificación local: 226 pruebas final y 128 M3 (354). El avance se mantiene 55–60 %; no se aumenta por otra preparación del juez.

Actualización vigente: [Comparación 02 auditada](evidence/comparison_02/ANALISIS.md), con [recálculo sin modelos](evidence/comparison_02/recalculated.json). No repetir inferencia. Completar [revisión humana de 44 respuestas reales](eval/review_comparison02/LEEME.md), resolver el juez para calificar las mismas respuestas, conectar dominio/controles, elegir configuración y desplegar el sistema real. El [reporte integrador](reporte.md) es borrador. Las notas anteriores de preparación se conservan como historial, no como tareas para volver a ejecutar.

Comparación 01 se conserva como fallo de interfaz. Comparación 02 sí completó la colección con la corrección; sus 110 registros no prueban por sí solos corrección semántica. Los porcentajes anteriores de 40–45 % correspondían a preparación sin esa evidencia. Verificación local vigente: 214 pruebas final y 128 M3 (342), sin nuevas inferencias para recalcular ni corregir telemetría.

La continuación 06 confirmó fallo real de aquel juez: una atribución falsa recibió 4 aunque el motivo la reconocía. Las pruebas API posteriores no lo validan: 07/08 quedaron sin notas, Hydrogen 09 produjo una nota adecuada en un único caso y 10 no agregó notas. El usuario autoriza USD 5 totales con preferencia por gratuito; no se activa facturación. El porcentaje no sube: falta cerrar los hitos, no solo preparar código o resolver formatos.

Verificación histórica de Hydrogen 10: 193 pruebas final y 128 M3 aprobadas (321), registradas en Colab. [Evidencia](evidence/hydrogen_10/ANALISIS.md): nota 2 conservada, 503 y reintento terminado por transporte/JSON, sin notas nuevas. USD 2,4706725 estimados/reservados, no factura. Las pruebas del cliente usan transporte simulado; no se aumenta el avance por una calibración todavía incompleta.

1. Ejecutar [recuperación 11 del juez en CPU](ContractRisk_Final_Juez_11_Recuperacion_Colab.ipynb), con secretos existentes y el mismo Drive. No repetir 07–10, seleccionar entre notas, borrar registros ni activar facturación. Preservar nota válida y USD 2,4706725 acumulados, dentro del techo TOTAL USD 5. La revisión de 44 respuestas fue recibida; adjudicar las ocho dudas sin rehacer el archivo completo. Las doce anclas están aprobadas, pero su ejecución y validación del juez siguen pendientes.
2. Conectar juicio validado y auditoría semántica/controles al harness común, recalificar las mismas respuestas guardadas y decidir eficiencia. No repetir Comparación 02 para buscar mejores resultados ni sustituir cobertura literal por dominio.
3. Elegir la configuración a desplegar según evidencia, integrar el Space real y comprobar salud/logs/W&B sin datos personales.
4. Escribir reporte/tablas/errores/ética/uso de IA, portada y diapositivas; acordar sustentación.
5. Reproducir desde limpio, revisar privacidad/accesos, PR y merge solo autorizado; entregar y conservar comprobante.

La guía pide repo/reporte antes del 19/11 a las 23:59 y sustentación hasta el 23/11; confirmar zona horaria/instrucciones particulares de Interactiva. El avance no se declara 100 % sin evidencias de cierre.
