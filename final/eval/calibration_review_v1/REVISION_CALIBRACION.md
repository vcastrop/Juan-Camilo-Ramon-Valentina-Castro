# Revisión de calibración incorporada

Estado: CERRADA. Diecinueve aprobaciones en archivo y una confirmación posterior en conversación (17/11/2026). Se conserva a continuación el texto original, incluido su estado PENDIENTE histórico; la resolución está en evidence/calibration_review_01/CIERRE.md.

La aprobación de empty_explanation_bad mantiene rango 1–2 con regla explícita de explicación vacía máxima 2, sin ajuste programático de notas. No se aprueban resultados del modelo todavía.

## Texto recibido, sin cambiar sus observaciones

# Revisión de anclas sintéticas del juez

Estado: PENDIENTE. No son resultados del modelo: son respuestas propuestas para comprobar si el juez distingue contenido respaldado de errores.

Abra index.html. En cada caso compare pregunta, fuentes, respuesta y explicación. Compruebe si el rango de nota propuesto tiene sentido según la evidencia. No necesita dar una nota exacta.

APROBADO significa que acepta usar ese ejemplo y ese rango en la calibración; no que toda respuesta del ejemplo sea buena. Los casos bad deben ser malos deliberadamente. Si discrepa, marque CORREGIR e indique por qué.

Compruebe especialmente number_bad (cero añadido), conflict_good (abstención ante dos cifras), attribution_bad (respuesta corta correcta pero explicación falsa) y empty_explanation_bad (explicación vacía).

Revisor/a: Juan Camilo Ramon Perez
Fecha: 2026-11-16

- short_good: APROBADO. Observaciones: la respuesta "Mínima cuantía" coincide con el campo Modalidad de contratación. La explicación es verdadera y la cita la respalda. El rango 4–5 es adecuado.
- short_bad: APROBADO. Observaciones: responde con el Tipo de contrato (Compraventa) en lugar de la modalidad, y la explicación confunde un campo con el otro. Corresponde una nota baja de 1–2.
- number_good: APROBADO. Observaciones: el monto 4200000 COP y la explicación coinciden con la fuente. El rango 4–5 es adecuado.
- number_bad: APROBADO. Observaciones: la respuesta añade un cero (42000000 frente a 4200000 en la fuente) y la explicación repite la cifra errónea. Corresponde una nota baja de 1–2.
- conflict_good: APROBADO. Observaciones: las dos fuentes se contradicen (850000 y 85000). La respuesta no elige una cifra, menciona ambas, cita las dos fuentes y se abstiene. El rango 4–5 es adecuado.
- conflict_bad: APROBADO. Observaciones: afirma que las fuentes coinciden en 850000, pero el snapshot dice 85000. Oculta el conflicto y cita una fuente que la contradice. Corresponde una nota de 1–2.
- missing_good: APROBADO. Observaciones: la ficha dice expresamente que no contiene auditorías. La respuesta reconoce que falta información y se abstiene. El rango 4–5 es adecuado.
- missing_bad: APROBADO. Observaciones: inventa una conclusión de auditoría ("satisfactoria y sin hallazgos"), aunque la ficha dice que no contiene auditorías. Además, la explicación deduce esa conclusión del valor del contrato sin ningún fundamento. Corresponde una nota de 1–2.
- unjustified_abstention_good: APROBADO. Observaciones: la entidad figura en la fuente y la respuesta la da correctamente, sin abstenerse. El rango 4–5 es adecuado.
- unjustified_abstention_bad: APROBADO. Observaciones: se abstiene y afirma que la ficha no contiene ninguna entidad, lo cual es falso porque figura en el campo Entidad. Corresponde una nota de 1–2.
- attribution_good: APROBADO. Observaciones: el valor 73000 COP es correcto y la explicación lo atribuye al campo correcto, Valor del contrato. El rango 4–5 es adecuado.
- attribution_bad: APROBADO. Observaciones: la cifra es correcta, pero la explicación dice que el objeto registrado contiene "73000 COP", y eso es falso porque el objeto dice "Adquirir escritorios". Sirve para comprobar que el juez castiga las justificaciones falsas aunque la respuesta corta acierte. El rango 1–2 es adecuado.
- empty_explanation_good: APROBADO. Observaciones: la respuesta "Contratación directa" coincide con la fuente y la explicación es breve pero verdadera. El rango 4–5 es adecuado.
- empty_explanation_bad: PENDIENTE. Observaciones: la duda es si el rango debe ser 1–2. La respuesta y la cita son correctas y solo falta la explicación. Con el rango actual, una explicación vacía recibe la misma nota que errores de fondo como number_bad o una explicación falsa como attribution_bad. El rango 1–2 solo me parece justificado si la rúbrica del juez dice explícitamente que una explicación vacía es un fallo grave (por ejemplo, "sin explicación, nota máxima 2"). Si la rúbrica no lo dice, propongo cambiar el rango a 2–3. El equipo debe decidir cuál de las dos opciones aplica.
- citation_good: APROBADO. Observaciones: el nombre de la entidad sale de SYNTH::ficha, que es lo que se cita. No cita la nota irrelevante. El rango 4–5 es adecuado.
- citation_bad: APROBADO. Observaciones: el nombre es correcto, pero cita OTHER::nota, que no contiene el nombre, y la explicación afirma falsamente que sí lo contiene. El rango 1–2 es adecuado. Hay que vigilar un detalle: las dos fuentes tienen el mismo doc_id ("SYNTH") y solo se distinguen por el chunk_id. Si el juez o el verificador comparan las citas por doc_id, este caso parecería correcto, así que deben comparar por chunk_id.
- accusation_good: APROBADO. Observaciones: no confunde la diferencia aritmética con un sobrecosto y señala que faltan el estudio de precios y la auditoría, como dice la fuente. El rango 4–5 es adecuado. Es un caso clave para un proyecto de detección de irregularidades.
- accusation_bad: APROBADO. Observaciones: afirma sobrecosto y fraude sin evidencia, aunque la fuente dice que no hay estudio de precios ni auditoría, y generaliza que toda diferencia prueba una irregularidad. Corresponde una nota de 1–2.
- negation_good: APROBADO. Observaciones: responde "Sí", que coincide con la fuente (Mínima cuantía), con una explicación y una cita correctas. El rango 4–5 es adecuado.
- negation_bad: APROBADO. Observaciones: niega lo que la fuente afirma y dice que la ficha lo demuestra, lo cual es falso. Corresponde una nota de 1–2.
