# Revisión humana pendiente: 12 casos separados

Actualización 18/11: [revisión recibida y cerrada](evidence/confirmation_review_01/CIERRE.md). No hace falta repetirla. Las instrucciones siguientes se conservan como procedimiento; inferencia y validación del juez siguen pendientes.

Esta revisión sí puede adelantarse mientras la API está indisponible. No requiere Colab, claves, GPU ni pagos. Los casos ya estaban fijados antes de los resultados del segundo candidato; no se cambian para lograr notas favorables. Revisarlos no valida por sí mismo al juez.

1. Descargar los archivos de `final/eval/confirmation_v1/` juntos o usar el ZIP de revisión proporcionado por este chat. Extraer el ZIP; no abrir el HTML dentro del archivo comprimido.
2. Abrir `index.html` en el navegador. Muestra la pregunta, evidencia, respuesta propuesta, explicación y rango de nota de cada caso.
3. Para cada uno de los doce casos, comprobar si el rango propuesto está justificado únicamente por sus fuentes. Los ejemplos `bad` contienen errores deliberados: aprobar su rango 1–2 significa reconocer el error, no aceptar la respuesta como correcta. Los `good` proponen 4–5; no aprobarlos automáticamente por su nombre.
4. Abrir `REVISION_CONFIRMACION.md` con un editor. Escribir nombre real del revisor y fecha real. En cada línea sustituir PENDIENTE por APROBADO o REQUIERE CAMBIO y explicar cualquier discrepancia. No modificar `anchors.json` ni los criterios para ocultar una discrepancia; comunicarla para resolverla antes de medir.
5. Solo si todos quedaron realmente revisados, actualizar el estado general. Enviar el Markdown revisado por este chat. Si alguna fuente, respuesta o rango no se entiende, dejar esa línea pendiente y preguntar.

No escribir que se ejecutaron estos 12 casos: su inferencia sigue pendiente. Una vez aprobados se registrarán la revisión y hashes; se ejecutarán únicamente después de que el candidato supere los controles anteriores. No hay aprobación humana registrada todavía.
