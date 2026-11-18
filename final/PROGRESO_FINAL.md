# Avance de la entrega final — 18/11/2026

Estimación operativa: **40–45 % (punto de referencia ~43 %)** de la entrega final integradora. No es nota, madurez para uso real ni porcentaje del curso completo. M1–M3 sirven de base, pero no sustituyen evaluación común, eficiencia, despliegue y documentos finales.

## Cómo se estima

Se ponderan hitos del checklist por esfuerzo/resultado, reconociendo avance parcial y separando código preparado de ejecución comprobada. Estos pesos son una herramienta interna de seguimiento, **no los puntos de la rúbrica académica**. Contar todas las casillas por igual sería engañoso: algunas preparatorias son pequeñas y una sola comparación o despliegue puede requerir mucho trabajo.

| Hito del checklist | Peso de seguimiento | Avance estimado | Evidencia o pendiente principal |
|---|---:|---:|---|
| Fase 0: insumos/base | 10 % | 80 % | Guía, rama, materiales disponibles, corpus/modelos y cuentas; inventario completo y responsabilidades pendientes. |
| Fase 1: producto e infraestructura | 10 % | 60 % | Modos/interfaz en código, Space inicial y GPU; servicio contractual público todavía no integrado. |
| Fase 2: integración de desarrollo | 20 % | 75 % | Texto/herramienta/M1 y visión probados en T4; guard de conflictos en CPU; seguridad/calidad y servicio final pendientes. |
| Fase 3: evaluación común | 15 % | 50 % | 22 entradas y 20 anclas aprobadas; continuación 06 rechazada. Harness candidato implementado en CPU, alternativa API preparada; aún sin juez validado ni protocolo/ejecución común cerrados. |
| Fase 4: eficiencia | 15 % | 15 % | Política aprobada y loader NF4 preparado; no hay medición antes/después ni decisión de aceptación. |
| Fase 5: comparativas/ablación/análisis | 10 % | 10 % | Fallos de desarrollo auditados; tabla común y ablación nuevas pendientes. |
| Fase 6: producción/observabilidad | 10 % | 25 % | Space de infraestructura y W&B de pruebas; faltan consultas contractuales reales desde despliegue. |
| Fase 7: reporte/presentación | 7 % | 10 % | Documentación de desarrollo disponible; faltan reporte integrador, portada, ética/IA y diapositivas finales. |
| Fase 8: cierre verificable | 3 % | 0 % | Pendientes clon limpio, revisión integral, PR/merge autorizado y entrega. |

Suma ponderada: ~42,95 %, redondeada a rango 40–45 % para no atribuir precisión falsa a estimaciones de esfuerzo. Se actualizará al cerrar hitos, no por número de pruebas añadidas.

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

Preparación más reciente: [revisión humana de doce ejemplos cerrada](evidence/confirmation_review_01/CIERRE.md). [Comparación 01](COMPARACION_01.md) preparada para cinco perfiles y 22 casos, sin API del juez, con reglas predeclaradas y mediciones CUDA sincronizadas. Verificación local: 206 pruebas final + 128 M3 = 334 aprobadas. Inferencia nueva todavía pendiente; el avance global permanece 40–45 %. No equivale a juez validado, cuantización aceptada, scorecard final o despliegue real.

La continuación 06 confirmó fallo real de aquel juez: una atribución falsa recibió 4 aunque el motivo la reconocía. Las pruebas API posteriores no lo validan: 07/08 quedaron sin notas, Hydrogen 09 produjo una nota adecuada en un único caso y 10 no agregó notas. El usuario autoriza USD 5 totales con preferencia por gratuito; no se activa facturación. El porcentaje no sube: falta cerrar los hitos, no solo preparar código o resolver formatos.

Verificación histórica de Hydrogen 10: 193 pruebas final y 128 M3 aprobadas (321), registradas en Colab. [Evidencia](evidence/hydrogen_10/ANALISIS.md): nota 2 conservada, 503 y reintento terminado por transporte/JSON, sin notas nuevas. USD 2,4706725 estimados/reservados, no factura. Las pruebas del cliente usan transporte simulado; no se aumenta el avance por una calibración todavía incompleta.

1. Ejecutar [Comparación 01 en T4](ContractRisk_Final_Comparacion_01_Colab.ipynb) y auditar respuestas/mediciones sin depender de la API. En tarea separada resolver disponibilidad con diagnóstico sanitizado antes de otra reanudación; no repetir 07–10, seleccionar entre notas, borrar registros ni activar facturación. Preservar nota válida y USD 2,4706725 acumulados. Los doce ejemplos están revisados, pero calibración/confirmación ejecutadas y auditoría del juez siguen pendientes antes de aceptar calidad.
2. Completar/congelar [harness común candidato](HARNESS_COMUN.md) y controles; ejecutar sistemas comparables, antes/después FP16/NF4 y ablación, con hashes y mismas condiciones.
3. Elegir la configuración a desplegar según evidencia, integrar el Space real y comprobar salud/logs/W&B sin datos personales.
4. Escribir reporte/tablas/errores/ética/uso de IA, portada y diapositivas; acordar sustentación.
5. Reproducir desde limpio, revisar privacidad/accesos, PR y merge solo autorizado; entregar y conservar comprobante.

La guía pide repo/reporte antes del 19/11 a las 23:59 y sustentación hasta el 23/11; confirmar zona horaria/instrucciones particulares de Interactiva. El avance no se declara 100 % sin evidencias de cierre.
