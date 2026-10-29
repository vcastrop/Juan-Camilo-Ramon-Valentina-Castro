# Núcleo de harness QA — candidato 0.1

> **Antecedente/candidato, no ruta vigente de entrega.** Consultar [RUTA_ENTREGA.md](RUTA_ENTREGA.md) y [CHECKLIST.md](CHECKLIST.md). La reevaluación RAGAS 1.1 del compañero ya se ejecutó; este documento no la reemplaza.

Implementado y probado con dobles sintéticos; NO ejecutado sobre el gold. No es el scorecard final. El juez no está aprobado y RAGAS todavía no está integrado. No publicar sus pruebas como resultados del modelo.

## Interfaz

`harness_qa.harness(eval_set, system, judge)` acepta una lista de casos, cualquier sistema con `predict(pregunta)` y un juez con `evaluate(record)`. El sistema recibe solo la pregunta; el juez recibe respuesta, contextos y trazas, nunca referencia, criterio gold ni acierto. La referencia se usa únicamente en la evaluación automática. La salida contiene una fila por caso y resumen versionado. Se registran errores sin eliminar preguntas del denominador.

## Tres dimensiones, con límites explícitos

1. **reference_token_f1_mean:** F1 multiconjunto de tokens de respuesta frente a referencia, promedio por pregunta. Se normalizan mayúsculas, tildes, puntuación y espacios. No se eliminan stopwords ni se equiparan números distintos. Vacío/esquema inválido/error del sistema vale 0. No es accuracy factual, Macro F1 de clases ni medida de verdad: penaliza paráfrasis correctas y puede dar crédito a textos parecidos pero incorrectos. La corrección humana de m3_004 admite paráfrasis: una nota lexical baja NO invalida por sí sola esa respuesta. No se usa un umbral para aprobarla.
2. **judge.mean_valid_only:** notas originales 1–5 del evaluador, con cantidad válida/faltante y tasas de parsing. Fallo del juez es nulo, nunca 0 ni 3 ni un reemplazo por regla. Un promedio sin cobertura no constituye evaluación completa. Juez definitivo y calibración siguen pendientes; el harness no convierte la presencia de todas las notas en aprobación de calidad.
3. **domain_traceability_rate:** proporción de salidas que cumplen el contrato ESTRUCTURAL de trazabilidad para un analista: respuesta/explicación no vacías, modo de abstención compatible con answerability, citas existentes con texto y fuente, IDs de contextos no ambiguos y cobertura de todos los documentos requeridos en preguntas respondibles. Para casos no respondibles se exige abstención; no se fuerza citar un documento ausente. Cálculos requieren citar ambos documentos.

La tercera dimensión NO verifica que el fragmento citado contenga el operando ni que implique la afirmación. Una respuesta falsa puede pasar trazabilidad: existe un test explícito que lo demuestra. No llamarla «cumplimiento semántico del dominio» ni «respuesta correcta». Es un control operativo distinto de similitud y del juicio semántico. El sustento se debe analizar mediante faithfulness/RAGAS y revisión; esta limitación debe mantenerse en el informe. Si se exige una medida semántica del criterio individual, este proxy no la sustituye y debe ampliarse antes de congelar.

## Tiempo y errores

Latencia medida alrededor de `system.predict`, sin juez; mediana sobre TODOS los intentos, también fallidos. Carga e indexación se registrarán en el runner aparte. No utilizar la reproducción de contextos v6 para la tabla de recuperación en vivo. No comparar resultados entre versiones del harness sin recalcular todas las filas.

La bandera `quality_approved` permanece falsa: no hay un criterio automático que permita aprobar la entrega. `all_judgements_available` solo mide disponibilidad, no validez semántica.

## Antes del scorecard final

- Decidir/congelar métricas y documentar adaptación de baseline QA.
- Seleccionar/calibrar evaluador; conservar v5/v6 como diagnóstico, sin sustituir notas.
- Integrar RAGAS con definiciones del curso y reglas explícitas de N/A.
- Añadir runner común, exportación CSV/JSON, metadatos y reconstrucción reproducible.
- Ejecutar las cuatro variantes en las mismas 12 preguntas; revisar citas, abstenciones y razones, incluyendo resultados negativos.
