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

La continuación 06 confirmó fallo real del juez: una atribución falsa recibe 4 aunque el motivo la reconoce. Se conservaron las siete notas previas y la nueva; no hubo error técnico. Harness común candidato y cliente API 07 con registro persistente preparados, sin inferencia API ni aceptación de calidad. El usuario guardó la clave en Colab y autoriza USD 5 totales, con preferencia por gratuito; el runner solo admite proyecto gratuito confirmado. El porcentaje no sube: falta cerrar y ejecutar los hitos, no solo preparar más código.

Verificación local vigente: 182 pruebas final y 128 M3 aprobadas (310). API 07/08 recibieron 503 sin notas. Hydrogen 09 preparado como candidato nuevo, historial y reservas preservados. Las cifras menores corresponden a etapas históricas; las pruebas del cliente usan transporte simulado. No se aumenta el avance por un servicio todavía sin evaluar.

1. Ejecutar [candidato Hydrogen 09](ContractRisk_Final_Juez_09_Hydrogen_Colab.ipynb) tras dos 503 y cero notas del modelo anterior. Mismo registro Drive, proyecto gratuito, [presupuesto acumulado](JUEZ_HYDROGEN_09.md) y criterios intactos. No repetir 07/08 ni seleccionar entre notas. Auditar calibración/confirmación antes de aceptar calidad.
2. Completar/congelar [harness común candidato](HARNESS_COMUN.md) y controles; ejecutar sistemas comparables, antes/después FP16/NF4 y ablación, con hashes y mismas condiciones.
3. Elegir la configuración a desplegar según evidencia, integrar el Space real y comprobar salud/logs/W&B sin datos personales.
4. Escribir reporte/tablas/errores/ética/uso de IA, portada y diapositivas; acordar sustentación.
5. Reproducir desde limpio, revisar privacidad/accesos, PR y merge solo autorizado; entregar y conservar comprobante.

La guía pide repo/reporte antes del 19/11 a las 23:59 y sustentación hasta el 23/11; confirmar zona horaria/instrucciones particulares de Interactiva. El avance no se declara 100 % sin evidencias de cierre.
