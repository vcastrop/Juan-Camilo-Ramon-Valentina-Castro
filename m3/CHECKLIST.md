# Checklist vigente — cierre de ContractRisk M3

Actualizado el 29/10/2026 al consolidar el bundle `bc93baa` en `Entrega/contractrisk-m3`. No modifica main.
Esta es la única lista operativa. El plan inicial y sus fases A–L se conservan en [HISTORIAL_CHECKLIST.md](HISTORIAL_CHECKLIST.md), sin convertir sus casillas antiguas en pendientes nuevos.

## Base experimental completada

- [x] Corpus de 24 fichas SECOP II, fuentes, manifiesto y pipeline de indexación.
- [x] Gold de 12 preguntas revisado por el equipo, con dos no respondibles.
- [x] Cuatro sistemas comparables y dos ablaciones ejecutados sobre el mismo gold.
- [x] Recuperación híbrida, filtro de ID y reranking implementados y medidos.
- [x] Herramienta de diferencia de valores, límites y trazas de llamadas.
- [x] Corrida original con 72 respuestas, harness, latencias y RAGAS preservada.
- [x] Harness 1.1: recálculo sobre respuestas congeladas, sin regenerar ni sustituir notas del juez.
- [x] RAGAS 1.1 del compañero ejecutado en T4: 36 casos, 393 llamadas, análisis de fallos del juez.
- [x] Reporte con arquitectura, tablas, ejemplos y limitaciones. Todavía requiere los ajustes del bloque 2.
- [x] Auditoría de desarrollo v6 y controles adicionales conservados como antecedentes/candidatos.

## Bloque 1 — consolidar la versión definitiva

- [x] Integrar los dos commits nuevos del compañero, sin reemplazar la rama completa.
- [x] Preservar corpus, gold, código original y evidencias brutas de ambas líneas de trabajo.
- [x] Establecer versión de referencia de cada tabla en [RUTA_ENTREGA.md](RUTA_ENTREGA.md).
- [x] Separar documentación histórica y candidatos sin borrar archivos ni romper imports.
- [x] Reemplazar instrucciones de traspaso desactualizadas por una ruta vigente.
- [x] Verificar pruebas combinadas: 120 aprobadas; 19 enlaces nuevos comprobados y 22 archivos originales de corpus/gold/evidencia bruta preservados. Código y resultados del compañero coinciden con el bundle.
- [ ] Publicar y comprobar el commit consolidado en la rama remota M3; no fusionar main.

## Bloque 2 — precisión del reporte

- [ ] Acotar «más confiable» a concordancia observada con un diagnóstico automático, no validación humana independiente.
- [ ] Acotar determinismo a coincidencia observada en las ejecuciones comparadas.
- [ ] Distinguir cobertura automática 8/10 y veredicto del juez 7/10, sin afirmar tres ausencias reales de información.
- [ ] Revisar que 0,611 se presente como cobertura media, no porcentaje de respuestas correctas.
- [ ] Declarar correcciones post-hoc y que el gold ya fue inspeccionado.
- [ ] Revisar que se distinga evidencia original de auditoría documental posterior.

## Bloque 3 — límites del evaluador

- [ ] Consolidar el diagnóstico de afirmaciones cortas omitidas, parser sí/no ambiguo, negación aproximada y datos faltantes.
- [ ] Decidir y documentar qué controles se conservan como limitaciones y cuáles justifican una nueva versión/corrida.
- [ ] No atribuir resultados existentes a reglas modificadas después de ejecutarlos.
- [ ] No cambiar notas del juez por comprobaciones de acierto.

## Bloque 4 — juez alternativo (opcional, no bloquea el cierre)

- [ ] Solo si se decide intentarlo: calibración separada del gold y criterios fijados antes de evaluar.
- [ ] Probar recursos y comportamiento antes de prometer una corrida completa.
- [ ] Repetir RAGAS sobre respuestas congeladas solo si la calibración resulta aceptable; conservar ambos resultados.
- [ ] Si se omite, declararlo como mejora futura, no como componente ejecutado.

## Bloque 5 — revisión y entrega

- [ ] Comprobar instrucciones completas desde entorno limpio, enlaces, versiones, licencias y ausencia de secretos.
- [ ] Confirmar aportes humanos reales en Uso de IA y revisar coherencia con M1/M2.
- [ ] Contrastar rúbrica: corpus, técnicas avanzadas, agente, harness, RAGAS y análisis.
- [ ] Revisar PR hacia main y fusionar solo con aprobación del equipo.
- [ ] Entregar enlace y conservar comprobante en Interactiva.
- [ ] Preparar explicación oral por ambos integrantes.

Avance orientativo de M3: alrededor de 90 % (85–90 %), no una nota ni una tasa de respuestas correctas.
No declarar el sistema apto para uso autónomo: conserva abstención 0/2 en avanzado/final y errores de generación y de juez.
