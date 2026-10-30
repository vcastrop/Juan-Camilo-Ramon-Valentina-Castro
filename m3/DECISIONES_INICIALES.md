# M3: alcance y decisiones iniciales

Estado: inicio de implementación, no entrega terminada. Fecha: 28 de octubre de 2026.

## Plazo y protección del trabajo anterior

- Plazo comunicado por el equipo: 29 de octubre de 2026, 23:59, America/Bogota. No se ha accedido a Interactiva para comprobarlo de forma independiente.
- Rama local nueva: `Entrega/contractrisk-m3`, creada desde main `5d82be9471baffb958096bd686a91124752691b5`.
- No se modifica ni se publica la rama experimental eliminada de M2. Los resultados históricos se conservan.
- Publicación y merge pendientes de revisión. No se garantiza completar una corrida por una estimación de tiempo: Colab, descargas y calidad del juez deben verificarse.

## Qué vamos a construir

Un asistente para consultar fichas públicas de contratación y justificar sus respuestas con evidencia. Ayuda al analista a entender qué información está disponible y qué requiere consultar en otro documento. Forma parte de la visión de priorización de contratos que ameritan revisión, pero no determina fraude, corrupción, sobrecostos ni ilegalidad.

El corpus inicial es una muestra intencional de 24 fichas públicas de SECOP II: cuatro por cada uno de seis tipos de contrato, filtradas por el campo `fecha_de_firma` en 2024. Esto describe el filtro de la fuente, no una verificación independiente de la fecha real de firma. Se excluyen los identificadores y descripciones idénticas normalizadas de M1/M2. Las fichas son datos reales convertidos a texto de forma determinista; NO son los documentos contractuales íntegros. Falta revisión del equipo y diagnóstico de recuperación antes de congelar el corpus. Se observaron fechas de inicio anteriores a la fecha de firma registrada: no se corrigen ni se interpretan automáticamente como irregularidad.

Preguntas previstas, cuya redacción final dependerá de las fuentes descargadas:

- Qué objeto o actividad se describe, qué entidad lo contrata y qué valor se registra.
- Qué modalidad y fechas aparecen en la ficha, citando su identificador.
- Qué diferencia de valor existe entre dos fichas identificadas, mostrando datos y operación.
- Qué información NO está disponible: obligaciones detalladas, sanciones, comprobación de ejecución u otras afirmaciones ausentes. Se debe abstener, sin convertir una ausencia en una acusación.

El corpus contiene las fuentes; el eval set contiene preguntas, referencias y criterios usados por el evaluador. No se indexarán respuestas gold, informes de evaluación ni etiquetas del equipo.

## Materiales de clase y adaptación

Se inspeccionaron las diapositivas S07/S08/S10 y el código relevante de los laboratorios resueltos, sin ejecutar sus celdas. Los notebooks vacíos se inventariaron junto a sus versiones resueltas. Los extras de W&B y DSPy se revisaron para determinar su alcance.

| Material | Uso en ContractRisk | Diferencia necesaria |
|---|---|---|
| S07 | Ingestión, chunks con fuentes, embeddings, Chroma, RAG ingenuo y abstención | Sustituir corpus educativo por fuentes reales. Medir el chunking del corpus: caracteres, palabras y tokens no son equivalentes |
| S08 | Búsqueda híbrida BM25+dense/RRF y reranking | Son las dos técnicas candidatas. Justificarlas con fallos observados en desarrollo y medir el resultado, incluso si no mejora |
| S10 | Llamadas de herramientas con esquema y límite de pasos; evaluación del contexto | Validar argumentos, conservar trazas, no usar `eval` para aritmética; decidir llamadas con el modelo y registrar errores |
| Extra W&B | Seguimiento opcional de experimentos | Primero conservar JSON/CSV locales reproducibles. No bloquear entrega con cuentas externas |
| Extra DSPy | Optimización opcional | Fuera del alcance inicial: exige evaluación fiable y separación desarrollo/test |

Punto de partida del curso, aún sin prueba en esta implementación: generador `Qwen/Qwen2.5-1.5B-Instruct`, embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, reranker `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`, Chroma y `rank_bm25`. Las versiones, revisiones de modelos, memoria y calidad se comprobarán antes de congelar configuración. No se presuponen resultados del material ilustrativo como resultados propios.

## Comparación válida para un proyecto originalmente clasificador

RoBERTalex de M1/M2 clasifica descripciones y no puede responder preguntas abiertas. Se preserva como módulo y benchmark histórico. La comparación QA propuesta usa el mismo generador y prompt base en cuatro condiciones: sin documentos recuperados, RAG ingenuo, RAG avanzado y RAG avanzado con herramienta. La primera fila se rotulará **control generativo sin RAG, adaptado al benchmark QA**: no se atribuirá a RoBERTalex ni se reutilizará su Macro F1 como resultado QA.

Esta adaptación se apoya en el permiso de la guía para formular preguntas nuevas cuando M1 era clasificación. Queda pendiente confirmar con el profesor la rotulación de la fila solicitada como baseline M2. Si no hay respuesta, se declarará explícitamente esta limitación y se mostrará el baseline histórico aparte, sin simular equivalencia.

## Evaluación: correcciones que deben implementarse

1. Generar respuesta y explicación con citas. El juez evalúa esa respuesta, no la riqueza del documento por sí sola.
2. Nunca reemplazar la nota por 4 si acierta o 1 si falla. Nunca enviar un indicador de coincidencia de etiquetas al juez.
3. No copiar el fallback `3` de los ejemplos de clase ante parsing fallido. Registrar valor ausente, salida original y tasa de fallos sobre todos los casos.
4. Rúbrica completa 1–5 y calibración separada del conjunto final, incluyendo explicaciones vacías, errores, aciertos y abstenciones.
5. Prueba de verbosidad con múltiples pares equivalentes y notas sin ajustar. No concluir ausencia general de sesgo por un caso.
6. Tres dimensiones con aportes distinguibles: métrica automática QA, juez real y cumplimiento verificable del criterio de dominio (hechos requeridos/citas o abstención según el caso). Definir reglas antes de la corrida, sin umbrales escogidos para mejorar resultados.
7. Cuatro métricas RAGAS, declarando implementación. La S10 ofrece una implementación didáctica propia: no equivale numéricamente a toda versión de la librería. Registrar decisiones por afirmación/pasaje, evitar valores perfectos automáticos para respuestas vacías y tratar casos no aplicables explícitamente.
8. Medir latencia del sistema por consulta, separada del costo del juez, y publicar la mediana. El ejemplo S08 calcula un promedio del harness: no copiarlo como si fuera la mediana solicitada.

## Secuencia con el plazo disponible

1. Esta noche: corpus candidato trazable, alcance, borrador de preguntas para revisión humana y base de ingestión/pruebas.
2. Luego: congelar fuentes y gold revisado; RAG ingenuo y diagnóstico de recuperación; corregir y calibrar evaluación.
3. Construir dos técnicas y herramienta acotada; pruebas locales y prueba corta real en T4 antes de la corrida completa.
4. Ejecutar todas las variantes con configuración congelada, guardar logs, scorecard y RAGAS, revisar razones del juez.
5. Reservar las últimas horas antes del plazo para análisis, README, declaración IA, revisión del PR, ejecución limpia y envío. No sustituir pasos sin ejecutar por texto que diga que se completaron.

## Trabajo humano necesario

- Revisar el borrador de preguntas, respuestas de referencia y citas contra las fichas. Aún no hay gold QA revisado.
- Ejecutar el notebook del proyecto en Colab T4 cuando esté listo y devolver notebook con salidas y ZIP.
- Confirmar los aportes realmente realizados por cada integrante para la declaración de IA y poder explicar el sistema.

## Uso de IA durante esta preparación

Se usó ChatGPT/Codex para revisar requisitos y materiales, proponer el plan, inspeccionar el repositorio y escribir el script inicial y sus pruebas. El equipo proporcionó materiales, comentarios del profesor y el plazo. La revisión humana de código, corpus y nuevas preguntas está pendiente; no se presenta como realizada.
