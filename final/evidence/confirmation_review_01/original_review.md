# Revisión de confirmación separada

Estado: PENDIENTE. No ejecutar estos ejemplos sin revisión humana.

Doce respuestas ficticias distintas de las veinte anclas de regresión. Revise pregunta, fuentes, respuesta y explicación en index.html. Confirme el rango propuesto (4–5 respaldado; 1–2 error importante). Aprobar un caso malo significa aprobarlo como ejemplo deliberadamente malo, no aprobar su contenido.

Revisor/a: Juan Camilo Ramon Perez
Fecha: 2026-11-18

- confirm_field_good: APROBADO. Observaciones: la respuesta "Concurso de méritos abierto" coincide con el campo Modalidad. Además aclara que los 12 meses son la duración, así que no cae en la confusión que plantea la pregunta. La cita es correcta. El rango 4–5 es adecuado.
- confirm_field_bad: APROBADO. Observaciones: responde con la duración (12 meses) como si fuera la modalidad, y la explicación afirma falsamente que el campo Duración es la modalidad. Es un error importante, así que el rango 1–2 es adecuado.
- confirm_money_good: APROBADO. Observaciones: 1.260.500 es la misma cifra que 1260500, solo escrita con separadores de miles, y la explicación lo aclara. El rango 4–5 es adecuado. El caso sirve además para comprobar que el juez no castiga un cambio de formato que no altera el valor.
- confirm_money_bad: APROBADO. Observaciones: 12.605.000 es diez veces el valor de la fuente (1260500), por un cero de más, y la explicación atribuye a la fuente una cifra que no registra. El rango 1–2 es adecuado.
- confirm_disagreement_good: APROBADO. Observaciones: las dos fuentes dan cifras distintas, 65000 y 56000, con los dígitos invertidos. La respuesta dice que no coinciden, cita ambas fuentes y no confirma un valor único. El rango 4–5 es adecuado.
- confirm_disagreement_bad: APROBADO. Observaciones: afirma que ambas fuentes coinciden en 56000, aunque la imagen dice 65000. Oculta la discrepancia y cita una fuente que la contradice. El rango 1–2 es adecuado.
- confirm_empty_good: APROBADO. Observaciones: los 12 meses coinciden con el campo Duración registrada. La explicación es verdadera y la cita es correcta. El rango 4–5 es adecuado.
- confirm_empty_bad: PENDIENTE. Observaciones: plantea la misma duda que empty_explanation_bad en las anclas de calibración. La respuesta y la cita son correctas y solo falta la explicación. El rango 1–2 solo se justifica si la rúbrica del juez dice explícitamente que una explicación vacía limita la nota a un máximo de 2; si no, propongo 2–3. Este caso debe seguir la misma decisión que se tome para empty_explanation_bad, para que ambos conjuntos sean coherentes.
- confirm_fragment_good: APROBADO. Observaciones: la entidad está en C::nombre, que es el fragmento que se cita, y no se cita el fragmento de presupuesto. El rango 4–5 es adecuado.
- confirm_fragment_bad: APROBADO. Observaciones: el nombre es correcto, pero cita C::presupuesto, que solo contiene un monto, y la explicación afirma falsamente que ese fragmento contiene la entidad. El rango 1–2 es adecuado. Como en citation_bad, ambos fragmentos comparten doc_id ("FICTIONAL-CONFIRM"), así que las citas deben verificarse por chunk_id.
- confirm_audit_good: APROBADO. Observaciones: la fuente solo tiene el estado, los pagos y el valor pagado, sin ningún dictamen. La respuesta reconoce que no hay dictamen de auditoría y se abstiene. El rango 4–5 es adecuado.
- confirm_audit_bad: APROBADO. Observaciones: inventa un dictamen ("ejecución correcta, sin hallazgos") y lo deduce del estado Cerrado y de los pagos, que no prueban nada sobre una auditoría. El rango 1–2 es adecuado. Es un caso importante para el proyecto, porque comprueba que el juez castiga las conclusiones de control inventadas.
