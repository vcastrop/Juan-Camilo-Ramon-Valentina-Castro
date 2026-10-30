# Revisión técnica de entrega M3 desde copia limpia

Fecha: 29/10/2026. Revisión asistida por Codex, no sustituye la declaración de revisión humana del equipo.

## Versión y alcance

Se integraron por fast-forward y publicaron `2d315a3` y `ae80777` en `Entrega/contractrisk-m3`. Se clonó esa rama directamente desde GitHub en una carpeta nueva. Commit auditado: `ae8077766391f903c47e7ded13feaeb56aae1a94`. Main permaneció en `5d82be9471baffb958096bd686a91124752691b5`.

No se modificaron sistemas, prompts, métricas, respuestas, gold ni notas del juez. No se ejecutó una nueva inferencia GPU ni una instalación completa de dependencias en Colab en esta revisión. Se distinguen las comprobaciones CPU nuevas de las corridas T4 ya conservadas.

## Comprobaciones realizadas

| Comprobación | Resultado |
|---|---|
| Pruebas desde el clon limpio | 128 aprobadas |
| Enlaces locales de README raíz, README M3, ruta, checklist, traspaso, corpus y juez | 49 comprobados, ninguno roto |
| Gold y predicciones | 12 preguntas, 2 no respondibles; 72 respuestas únicas con preguntas coincidentes |
| Recálculo harness 1.1 | Ejecutado sobre las respuestas guardadas; 72 filas y tablas reproducidas, comparando texto con saltos de línea normalizados |
| RAGAS 1.1 | Agregados recalculados desde 36 registros; coinciden con CSV; 393 llamadas y 0 errores de parseo registrados |
| Tablas numéricas del README | 6 filas de harness, 6 de recuperación, 3 de RAGAS 1.0 y 3 de RAGAS 1.1 verificadas contra detalle/denominadores |
| Corpus offline | Reconstruido desde snapshot; documentos y snapshot idénticos byte a byte |
| Fragmentación | 133 chunks reconstruidos; contenido coincide con la corrida original |
| Notebooks de reproducción final y RAGAS 1.1 | Celdas de código compiladas y rutas/configuración inspeccionadas; no ejecutadas nuevamente en T4 |
| Credenciales | 148 archivos de texto M3/README raíz revisados con patrones específicos de tokens y claves; ninguna coincidencia |
| Rutas locales | Sin dependencias de rutas personales Windows en los scripts/documentos de entrada inspeccionados |

El escaneo de credenciales no es una auditoría de todo el historial Git, archivos binarios ni una garantía absoluta. Las rutas de runtime en logs originales son evidencia, no dependencias del usuario.

Se abrieron las páginas externas de [SECOP II](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h), su [vista de datos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/data_preview) y [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode). El portal de datos es dinámico: acceso al enlace no equivale a probar cada descarga. La reproducción auditada usa el snapshot congelado. Se revisaron atribución/licencia declarada y revisiones de modelos; no es un dictamen legal.

Evidencia CPU: [auditoría estructurada](evidence/delivery_review_ae80777/audit.json), [pruebas](evidence/delivery_review_ae80777/tests.log), [script de comprobación](evidence/delivery_review_ae80777/verify.py). El script recibe la raíz del clon y una carpeta de salida nueva; requiere el entorno Python de análisis con numpy. No requiere modelos GPU.

## Correspondencia con la guía M3

| Requisito | Evidencia | Límite o riesgo pendiente |
|---|---|---|
| Corpus, fuente, condiciones y decisiones de índice | corpus/, ingest.py, README secciones 1–2; reconstrucción offline y corrida T4 | Fichas, no contratos completos; revisión humana de privacidad confirmada en [constancia](evidence/REVISION_PRIVACIDAD_CORPUS.md) |
| RAG ingenuo conservado y válvula de escape | sistemas_m3.py, prompt y respuestas guardadas | Válvula implementada pero falla: avanzado/final 0/2. No certificar cumplimiento conductual perfecto |
| Dos técnicas por diagnóstico | Híbrido/RRF/filtro ID, reranking, ablaciones y ejemplos | Recuperar la ficha no garantiza recuperar el dato |
| Herramienta, esquema, parseo y límites | contract_tools.py, agent_v5.py, trazas de 2 cálculos y decisiones sin herramienta | Llamada innecesaria de m3_009 declarada |
| Tabla común con tres dimensiones y latencia | 12 casos, 6 variantes, tablas 1.1 y registros originales | La fila sin RAG es adaptación QA con Qwen, no el clasificador RoBERTalex original de M2; no ocultar la adaptación |
| Cuatro métricas RAGAS | ragas_m3_v11.py, resultados T4 y referencia/contexto por caso | Juez deficiente, métricas N/A según política y segmentación corta omitida; límites documentados, no resueltos |
| Reporte y lectura honesta | README: diagrama, tablas, latencias, errores y abstención | No inferir calidad global de coincidencia léxica ni de un juez no validado |
| Reproducibilidad | Versiones, seeds, commits, logs, notebooks y rutas | Verificación CPU nueva más corridas T4 históricas; no se promete identidad de inferencia entre entornos |
| Uso de IA y entrega | Sección Uso de IA, USO_DE_IA.md y CHECKLIST.md | Declaración aportada y confirmada; PR, fusión y envío en Interactiva no se dan por completados |

La guía admite resultados imperfectos explicados, pero exige elementos funcionales. Esta matriz acredita evidencia disponible, no garantiza una calificación ni declara solucionada la abstención.

## Observaciones y decisiones

1. `corpus/README.md` y el manifiesto conservan estados iniciales de candidato. Se aclara el estado técnico actual en el README sin alterar el manifiesto o los hashes. La revisión del gold no implica automáticamente una revisión humana de privacidad: esta última fue confirmada separadamente por Juan Camilo Ramón Pérez para las 24 fichas, con fecha 29/10/2026. [Constancia y límites](evidence/REVISION_PRIVACIDAD_CORPUS.md).
2. Los notebooks pueden clonar una rama móvil. La ruta de entrega indica cómo reconstruir un commit en un clon separado. Mientras se usen esos notebooks, no borrar la rama M3. El notebook final produce 1.0; el recálculo y notebook RAGAS separado producen las tablas 1.1.
3. El notebook RAGAS admite ZIP y clonación. Para la rama publicada, usar `USE_ZIP = False`, como indica RUTA_ENTREGA.md. No subir un ZIP de resultados como si fuera código.
4. Las verificaciones no autorizan reescribir resultados ni cambiar las reglas. Juez alternativo pospuesto; no es necesario repetir corridas por cambios documentales.
5. La declaración detallada de contribuciones humanas fue aportada y confirmada por los autores con fecha 29/10/2026; está enlazada desde el README. Quedan aprobación/fusión de PR y entrega. La revisión de privacidad cuenta con confirmación explícita del revisor; no marcar los demás pasos a nombre del equipo.
