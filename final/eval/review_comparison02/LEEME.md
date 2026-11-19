# Revisión de 44 respuestas reales

Actualización: [revisión recibida](../../evidence/human_response_review_01/RECEPCION.md), 44 casos cubiertos y ocho con dudas abiertas. No hace falta repetir todo el archivo. Las instrucciones siguientes se conservan como procedimiento de la plantilla inicial.

Esta revisión es distinta de las doce anclas sintéticas ya aprobadas. Ahora revisamos 22 respuestas reales del sistema FP16 y las mismas 22 de NF4. No hace falta Colab, GPU, claves ni pagos.

1. Extraer el ZIP completo y abrir index.html. Mantener la carpeta images al lado.
2. Cada pregunta tiene dos secciones, una por perfil. Consultar imagen original cuando exista, fuentes, respuesta, explicación y criterio. La lectura del VLM no sustituye a la imagen original ni acredita autenticidad.
3. Completar REVISION_RESPUESTAS.md con nombre y fecha reales. Para cada criterio indicar SI, NO o DUDOSO y justificar problemas. No marcar todo por el nombre del perfil ni por un porcentaje automático.
4. Respuesta respaldada: lo afirmado coincide con la evidencia. Explicación: sus afirmaciones también son verdaderas y suficientes, no basta con acertar el dato corto. Completa: responde todas las partes pedidas, por ejemplo modalidad y monto. Citas: el fragmento exacto contiene el respaldo; existir no basta.
5. Abstención adecuada: si responde con datos, marcar SI cuando responder está justificado; si se abstiene, SI solo cuando está justificado. Una abstención prudente por un error de lectura puede ser más segura sin resolver la tarea de una imagen legible: dejarlo explicado, sin cambiar la referencia para hacerla pasar.
6. Fallos críticos: usar NINGUNO, DUDOSO o los códigos del JSON adjunto. Son categorías predeclaradas; si una falla no encaja, escribirla en observaciones sin inventar códigos para penalizar después de ver resultados. No contar como cifra falsa de respuesta final una extracción equivocada que el sistema detectó y bloqueó.
7. No asignar notas del LLM, modificar las respuestas o declarar listo el sistema. Enviar el Markdown revisado; las dudas pueden permanecer abiertas.

Los diagnósticos literales y las observaciones de la IA no sustituyen esta revisión humana. El juez validado sigue pendiente; esta revisión no se presentará como si fuera una corrida LLM. Las respuestas almacenadas no se regeneran para elegir otras favorables.
