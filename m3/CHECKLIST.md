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
- [x] Reporte con arquitectura, tablas, ejemplos y limitaciones; ajustes del bloque 2 incorporados.
- [x] Auditoría de desarrollo v6 y controles adicionales conservados como antecedentes/candidatos.

## Bloque 1 — consolidar la versión definitiva

- [x] Integrar los dos commits nuevos del compañero, sin reemplazar la rama completa.
- [x] Preservar corpus, gold, código original y evidencias brutas de ambas líneas de trabajo.
- [x] Establecer versión de referencia de cada tabla en [RUTA_ENTREGA.md](RUTA_ENTREGA.md).
- [x] Separar documentación histórica y candidatos sin borrar archivos ni romper imports.
- [x] Reemplazar instrucciones de traspaso desactualizadas por una ruta vigente.
- [x] Verificar pruebas combinadas: 120 aprobadas (128 tras añadir `test_limites_m3.py` en el cierre de los bloques 2 y 3); 19 enlaces nuevos comprobados y 22 archivos originales de corpus/gold/evidencia bruta preservados. Código y resultados del compañero coinciden con el bundle.
- [x] Publicar el commit consolidado `f3d7ea8` en la rama remota M3 (push completado por el equipo); no fusionar main.
- [x] Integrar y publicar `2d315a3` y `ae80777`; clon remoto limpio verificado en `ae80777`, sin modificar main.

## Bloque 2 — precisión del reporte

- [x] Acotar «más confiable» a concordancia observada con un diagnóstico automático, no validación humana independiente.
- [x] Acotar determinismo a coincidencia observada en las ejecuciones comparadas.
- [x] Distinguir cobertura automática 8/10 y veredicto del juez 7/10, sin afirmar tres ausencias reales de información (revisión manual: 2 ausencias parciales, m3_004 y m3_006; m3_002 es falso negativo del juez).
- [x] Revisar que 0,611 se presente como cobertura media, no porcentaje de respuestas correctas.
- [x] Declarar correcciones post-hoc y que el gold ya fue inspeccionado.
- [x] Revisar que se distinga evidencia original de auditoría documental posterior (solo `results/final_m3/ANALISIS.md` cambió; datos brutos verificados sin cambios).

## Bloque 3 — límites del evaluador

- [x] Consolidar el diagnóstico de afirmaciones cortas omitidas, parser sí/no ambiguo, negación aproximada y datos faltantes: tabla «Qué comprueban y qué no» del README con el efecto medido en esta corrida (filtro corto: 6 casos; sí/no ambiguo: 0).
- [x] Decidir y documentar qué controles se conservan como limitaciones y cuáles justifican una nueva versión/corrida: se conservan todos como limitaciones de 1.1, fijadas por `tests/test_limites_m3.py`; ninguna nueva versión antes de entregar.
- [x] No atribuir resultados existentes a reglas modificadas después de ejecutarlos (no se cambiaron reglas en este cierre).
- [x] No cambiar notas del juez por comprobaciones de acierto.

## Bloque 4 — juez alternativo: POSPUESTO, no se ejecutará para esta entrega

Decisión del equipo: no se intenta en M3. Queda como mejora futura, declarada así en el README; no se presenta como componente ejecutado. Si se retoma (M4/M5), seguir estos pasos:

- Calibración con ejemplos separados del gold y criterios de aceptación fijados antes de evaluar.
- Probar memoria, tiempo y comportamiento antes de comprometer una corrida completa.
- Repetir RAGAS sobre las respuestas congeladas solo si la calibración es aceptable, y conservar ambos resultados.
- Identificarlo como evaluación distinta del juez de la dimensión 2 del harness.

## Bloque 5 — revisión y entrega

- [x] Auditar una copia limpia de GitHub: 128 pruebas, 49 enlaces locales, corpus/chunks reconstruidos, recálculo de tablas, sintaxis de notebooks, declaraciones de licencia y escaneo acotado de credenciales. [Registro y límites](REVISION_ENTREGA.md).
- [x] Revisar tablas del README frente a evidencia: 6 filas harness, 6 recuperación, 3 RAGAS 1.0 y 3 RAGAS 1.1.
- [x] Confirmar por el equipo la revisión de privacidad del texto libre del corpus: Juan Camilo Ramón Pérez declaró haber revisado las 24 fichas el 29/10/2026 sin identificar datos personales ni delicados. [Constancia y alcance](evidence/REVISION_PRIVACIDAD_CORPUS.md); distinta de la revisión del gold.
- Nueva ejecución integral T4 desde cero: no realizada en esta auditoría CPU; se conservan las corridas ejecutadas originales. No marcarla como prueba nueva.
- [x] Incorporar la declaración de aportes humanos y uso de IA facilitada y confirmada por los autores el 29/10/2026: [detalle](USO_DE_IA.md). No reemplaza las declaraciones históricas de M1/M2.
- [x] Contrastar rúbrica: corpus, técnicas avanzadas, agente, harness, RAGAS y análisis. [Cierre requisito por requisito y salvedades](CIERRE_REQUISITOS.md); revisión completada no equivale a cumplimiento conductual perfecto ni garantiza todos los puntos.
- [ ] Revisar PR hacia main y fusionar solo con aprobación del equipo.
- [ ] Entregar enlace y conservar comprobante en Interactiva.
- [ ] Preparar explicación oral por ambos integrantes.

Avance orientativo de M3: alrededor de 90–95 % de la entrega académica, no una nota, ni una tasa de respuestas correctas, ni madurez para uso real.
No declarar el sistema apto para uso autónomo: conserva abstención 0/2 en avanzado/final y errores de generación y de juez.
