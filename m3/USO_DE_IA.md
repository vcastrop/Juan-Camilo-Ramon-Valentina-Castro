# Uso de IA y aportes humanos — Entrega M3

Autores: **Juan Camilo Ramón Pérez** y **Valentina Castro Pineda**.

Herramientas de IA usadas para **construir** la entrega: **ChatGPT/Codex** (OpenAI) y **Claude Code** (Anthropic). Los modelos que forman parte del sistema (Qwen2.5-3B-Instruct como generador y juez, MiniLM multilingüe para embeddings y el cross-encoder mMiniLM) no cuentan como esta declaración.

Criterio general:
- La IA se usó sobre todo para escribir y mejorar código, generar pruebas, verificar que el código funcionara, auditar las salidas de las corridas y redactar borradores de documentación.
- El equipo definió el proyecto y las decisiones, ejecutó las corridas, revisó los resultados y validó los datos de referencia.
- El equipo revisó el gold y los resultados principales. La IA y las comprobaciones automáticas apoyaron la auditoría técnica.
- Una prueba automática aprobada no se consideró equivalente a una revisión humana del contenido.

> Distribución individual revisada y confirmada por ambos autores el 29/10/2026. Las tareas sin un responsable individual registrado se atribuyen al equipo en conjunto.

---

**Bloque 1 — Planeación y requisitos**
- **Juan:** leyó la guía de M3 y los materiales S07, S08 y S10. Decidió con Valentina adaptar ContractRisk a preguntas sobre contratos mediante RAG.
- **Valentina:** participó en la lectura de la guía, en la definición de objetivos y alcance, y en las decisiones sobre qué corregir y qué dejar como limitación o trabajo futuro.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** resumió requisitos de la guía, propuso una arquitectura por etapas y un checklist, y señaló riesgos (por ejemplo, la comparación con la línea base de M2).
- **Qué revisamos o modificamos nosotros:** validamos los requisitos contra la guía original, elegimos el alcance (consulta de fichas con fuentes, sin detectar fraude) y decidimos qué correcciones implementar y cuáles documentar como limitación.

**Bloque 2 — Corpus de contratos**
- **Juan:** eligió SECOP II como fuente, revisó la selección de 24 fichas en seis tipos y los campos usados. Realizó la **revisión de privacidad de las 24 fichas el 29/10/2026**.
- **Valentina:** participó en la revisión de las limitaciones del corpus: son fichas de registro, no contratos completos ni informes de auditoría.
- **IA utilizada:** ChatGPT/Codex.
- **Qué hizo la IA:** escribió el script de descarga y reconstrucción (`prepare_corpus.py`), la serialización «campo: valor», la comprobación de duplicados frente a M1/M2 y el registro de procedencia, licencia y hashes.
- **Qué revisamos o modificamos nosotros:** verificamos que las fichas fueran reales y trazables a SECOP II, que la licencia estuviera bien atribuida y que no hubiera datos personales innecesarios.

**Bloque 3 — Preguntas y respuestas de referencia (gold)**
- **Juan:** **leyó y validó** las 12 preguntas, sus respuestas esperadas y criterios contra las fichas, revisó las 24 fichas para confirmar que las dos preguntas sin respuesta realmente no tienen respuesta en el corpus y **corrigió `m3_004`** (respuesta truncada en la ficha), con fecha 28/10/2026. Su revisión está preservada en `eval/gold_v1/evidence/`.
- **Valentina:** participó en la definición de los tipos de pregunta: datos concretos, cálculo, inconsistencia de fechas y casos sin respuesta.
- **IA utilizada:** ChatGPT/Codex.
- **Qué hizo la IA:** **redactó el borrador** de preguntas, respuestas esperadas y criterios, y el script para congelar el gold con hashes.
- **Qué revisamos o modificamos nosotros:** el borrador de la IA no se aceptó como anotación humana. Cada caso se comparó con su ficha, se corrigieron respuesta y criterio donde hacía falta (`m3_004`) y se aprobó el conjunto final antes de congelarlo. El gold nunca se usó para ajustar prompts.

**Bloque 4 — Indexación y recuperación**
- **Juan y Valentina:** decidieron las técnicas a partir de los fallos observados del RAG ingenuo (no llegaba la ficha pedida y el ID no anclaba en el embedding). Revisaron qué fichas y fragmentos se recuperaban en cada corrida.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** ayudó a implementar y mejorar:
  - el chunking (versión final de 133 chunks);
  - los embeddings y el índice en Chroma;
  - BM25, la fusión RRF, el filtro por identificador y el reranking.

  También escribió pruebas de estos componentes. Claude Code añadió las ablaciones y el diagnóstico que separa «ficha correcta recuperada» de «dato necesario en el contexto».
- **Qué revisamos o modificamos nosotros:** contrastamos las recuperaciones con las fichas y aceptamos las técnicas solo después de ver su efecto en las corridas. También revisamos el hallazgo de la auditoría técnica asistida por IA de que recuperar la ficha correcta no implicaba recuperar el campo de valor.

**Bloque 5 — Generación de respuestas**
- **Juan y Valentina:** revisaron ejemplos de respuestas incorrectas, incompletas o sin respaldo en cada versión (v2 a v5) y decidieron qué ajustar. Revisaron y documentaron el **fallo de abstención** en los dos casos finales sin respuesta, incluida la auditoría inventada en `m3_012`.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** ayudó a:
  - configurar Qwen con revisión fija;
  - redactar y ajustar los prompts;
  - definir la salida estructurada (respuesta, explicación, citas, abstención);
  - escribir el validador y las pruebas de formato.
- **Qué revisamos o modificamos nosotros:** comprobamos con las salidas reales que el formato válido no significaba respuesta correcta y conservamos los fallos sin corregirlos a mano. Decidimos no ajustar el sistema contra el gold final.

**Bloque 6 — Agente y herramienta**
- **Juan y Valentina:** definieron el caso de uso de la herramienta (diferencia de valores entre dos fichas) y cuándo debía o no llamarse. Analizaron los cálculos correctos, la explicación errónea de `m3_007` y las llamadas innecesarias de `m3_009`.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** implementó la herramienta con aritmética `Decimal` y devolución de fuentes, el router con tope de pasos y bloqueo de llamadas repetidas, el registro de trazas y sus pruebas (llamada válida, inválida, duplicada y con timeout).
- **Qué revisamos o modificamos nosotros:** verificamos a mano que 168.000.000 y 15.387.424 COP fueran correctos según las fichas, revisamos las trazas y decidimos reportar las llamadas de más como hallazgo.

**Bloque 7 — Sistemas y experimentos comparativos**
- **Juan y Valentina:** decidieron comparar cuatro sistemas con el mismo generador y prompt, y añadir dos ablaciones. Interpretaron qué mejora se puede atribuir a cada componente.
- **IA utilizada:** Claude Code (y ChatGPT/Codex en las versiones de desarrollo).
- **Qué hizo la IA:** escribió `sistemas_m3.py` con una interfaz común, el script de la corrida final, el registro de respuestas, contextos, citas, latencias y trazas, y el cálculo de tablas.
- **Qué revisamos o modificamos nosotros:** ejecutamos las seis variantes sobre el mismo gold y revisamos que las cifras de las tablas correspondieran al detalle por caso.

**Bloque 8 — Harness de evaluación**
- **Juan y Valentina:** revisaron que el juez no recibiera la referencia ni indicadores de acierto y que no se reemplazaran sus notas. Aceptaron las correcciones y exigieron que se declararan como post-hoc.
- **Origen de los hallazgos:** la revisión técnica asistida por IA identificó errores del evaluador (números dentro de otros números, negaciones) y la interpretación excesiva de la cobertura; el equipo revisó los hallazgos.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** implementó la cobertura de hechos, el juez con rúbrica y justificaciones, el chequeo de dominio, el harness 1.1 y el recálculo sobre respuestas guardadas. Escribió pruebas que reproducen los defectos y fijan las limitaciones que se conservan.
- **Qué revisamos o modificamos nosotros:** confirmamos con casos concretos que los defectos existían, revisamos que el recálculo no regenerara respuestas ni notas, y exigimos que «0,611» se presentara como cobertura y no como exactitud.

**Bloque 9 — RAGAS y auditoría del juez**
- **Juan y Valentina:** compararon las variantes del laboratorio S10 con las adaptadas, revisaron las decisiones del juez frente a los hechos del contexto y **decidieron posponer el juez alternativo**: **no se ejecutó** y queda como mejora futura.
- **IA utilizada:** Claude Code (y ChatGPT/Codex en un candidato de auditoría no ejecutado).
- **Qué hizo la IA:** implementó RAGAS 1.0 y 1.1 (segmentación corregida y variantes por separado). Auditó las salidas del juez: detectó el «No» a los 94 pasajes, la concordancia de 28/30 del context recall y las afirmaciones cortas omitidas.
- **Qué revisamos o modificamos nosotros:** ejecutamos las corridas, verificamos a mano los desacuerdos (por ejemplo, `m3_002`) y aceptamos presentar RAGAS como diagnóstico provisional, no como confirmación de mejora.

**Bloque 10 — Ejecuciones y resolución de errores**
- **Juan:** manejó las ejecuciones en Colab con GPU T4: pruebas de desarrollo, protocolo, integración, corrección, la corrida final y las reevaluaciones. Descargó y compartió los notebooks ejecutados y los ZIP de resultados, y aplicó el arreglo de SQLite/FTS5 en Colab.
- **Valentina:** participó en la revisión de los resultados de cada iteración antes de continuar.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** diagnosticó errores a partir de los logs (por ejemplo, SQLite sin FTS5 y el directorio de trabajo inexistente en Colab), propuso y programó las soluciones, y auditó cada ZIP de resultados (hashes, integridad y conteos).
- **Qué revisamos o modificamos nosotros:** decidimos cuándo repetir una corrida y cuándo conservar el fallo como evidencia. Revisamos las salidas antes de avanzar y exigimos conservar las versiones históricas y separar los candidatos no adoptados.

**Bloque 11 — Pruebas y reproducibilidad**
- **Juan y Valentina:** revisaron que las pruebas cubrieran los casos relevantes y dirigieron la verificación de hashes y la correspondencia entre código y resultados.
- **IA utilizada:** ChatGPT/Codex y Claude Code.
- **Qué hizo la IA:** creó y amplió las pruebas automáticas (128 en la versión consolidada) y ejecutó las verificaciones de hashes, versiones, reconstrucción de corpus e índice, recálculo de tablas y revisión de enlaces, rutas y credenciales.
- **Qué revisamos o modificamos nosotros:** no tomamos las pruebas aprobadas como sustituto de la revisión del contenido. Revisamos tablas y evidencias por nuestra cuenta, y la comprobación desde entorno limpio se registra aparte en el checklist.

**Bloque 12 — Análisis y documentación**
- **Juan y Valentina:** revisaron y corrigieron el README, las tablas y la lectura honesta, revisaron los casos de error y abstención, y registraron la revisión de privacidad y esta declaración.
- **Origen de los hallazgos:** las afirmaciones excesivas se identificaron durante la revisión técnica asistida por IA y fueron revisadas por el equipo.
- **IA utilizada:** Claude Code y ChatGPT/Codex.
- **Qué hizo la IA:** redactó los **borradores** del README, el diagrama, la metodología, las auditorías, el checklist, la ruta de entrega y los documentos de traspaso.
- **Qué revisamos o modificamos nosotros:** corregimos las afirmaciones excesivas (cobertura no es exactitud, ficha recuperada no implica dato recuperado, coincidencia entre ejecuciones no garantiza determinismo, ausencias reales 2/10 y no 3/10). Exigimos documentar los límites del sistema y del evaluador, y aprobamos la versión final del texto.

**Bloque 13 — Integración y entrega**
- **Juan:** trabajó en la rama M3 sin modificar `main`. Recibió, revisó e integró los bundles de Claude Code conservando las evidencias v6 de su línea de trabajo, hizo los commits y la publicación de la consolidación.
- **Valentina:** es propietaria del repositorio. Participó en la revisión del PR y en la autorización de la fusión.
- **Juan y Valentina:** preparan la entrega del enlace en Interactiva y la explicación oral; ambos deben poder explicar arquitectura, métricas, decisiones y errores.
- **IA utilizada:** Claude Code y ChatGPT/Codex.
- **Qué hizo la IA:** generó los commits y bundles de su trabajo, ya que no tenía permiso de escritura en el repositorio, y ayudó a conciliar las dos líneas de desarrollo sin reemplazar evidencias.
- **Qué revisamos o modificamos nosotros:** decidimos qué integrar y en qué orden, verificamos los bundles antes de integrarlos y publicamos los cambios. La fusión a `main` se hace solo con aprobación de ambos.
