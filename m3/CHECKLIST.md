# ContractRisk Colombia: ruta de trabajo M3 y correcciones de M2

Plan inicial: 28 de octubre de 2026. Estado actual: gold humano congelado y comparación de desarrollo v2 ejecutada y auditada en T4. Agente implementado y probado localmente, pendiente prueba real; juez corregido y evaluación final pendientes.

## Estado vigente — corrida de desarrollo v2

**Última evidencia: v4 auditada, sin aprobación de calidad.** [Análisis v4](evidence/development_v4/ANALISIS.md): 10/32 salidas válidas inicialmente, 16/32 finalmente; ninguno de los 54 intentos alcanzó el límite de tokens. Dos cálculos ejecutados correctamente, pero salida final inválida y ninguna decisión válida sin herramienta. Prueba controlada de protocolo/generador pendiente antes del gold; no repetir v4 sin cambios. Los estados v2/v3 siguientes son antecedentes.

- [x] Preservar y auditar notebook y ZIP v4; comprobar hashes, fuentes y logs.
- [ ] Validar una configuración candidata en prueba pequeña de esquema, abstención, cifras y selección de herramienta; congelar después, no antes.
- [x] Preparar prueba sintética controlada de protocolo/modelo, con expectativas fuera de inferencia y casos separados del gold. [Plan y límites](PRUEBA_PROTOCOLO.md), 56 pruebas locales aprobadas. Inferencia y revisión semántica pendientes.

**Actualización posterior: desarrollo v3 ejecutado y auditado.** [Evidencia y diagnóstico](evidence/development_v3/ANALISIS.md). 32 registros, 18 salidas válidas de esquema. Herramienta ejecutada correctamente en dos cálculos, pero respuestas finales inválidas; cinco llamadas innecesarias rechazadas y ningún caso de decisión answer válida del controlador. No se cierra H ni la evaluación final. Estado v2 abajo conservado como antecedente.

- [x] Recibir y preservar ZIP y notebook v3 ejecutado; verificar hashes y fuentes.
- [x] Separar éxito técnico de calidad: documentar fallos de generación, abstención y controlador.
- [x] Corregir serialización compacta, formatos inequívocos del controlador y registro de terminación; probar sobre trazas v3. Implementación v4, 50 pruebas locales; [cambios y límites](CORRECCIONES_V4.md). Pendiente validar eficacia con modelo real.
- [ ] Repetir desarrollo y demostrar dos respuestas válidas con herramienta y una decisión válida sin llamada.

Evidencia: [análisis y artefactos originales](evidence/development_v2/ANALISIS.md). Las notas de avances anteriores que siguen son HISTÓRICAS: sus pendientes ya resueltos no sustituyen este estado ni las casillas actualizadas.

- [x] Conservar ZIP y notebook ejecutado sin alterar sus salidas.
- [x] Auditar 15 salidas: formato válido; cuatro preguntas por variante y prueba adicional de contexto vacío.
- [x] Comprobar correspondencia de código ejecutado con el paquete entregado y fragmentos con corpus.
- [x] Medir denso (0/4), híbrido con filtro ID (3/4) e híbrido con filtro ID y reranking (3/4).
- [x] Documentar que reranking recupera evidencia en 4/4, pero no mejora aciertos finales frente al híbrido en esta muestra.
- [ ] Validar abstención ante evidencia irrelevante: solo se superó la prueba de contexto vacío.
- [ ] Completar agente, juez independiente, métricas finales y RAGAS; ejecutar las cuatro filas sobre gold.

Estas casillas no certifican calidad general ni cierre de M3. Main permanece intacto.

## Historial de preparación (no estado vigente)

Plazo comunicado por el equipo: **29 de octubre de 2026, 23:59, America/Bogota**. No verificado de forma independiente en Interactiva.

Avance del 28 de octubre: materiales del curso inventariados y código relevante inspeccionado; rama local `Entrega/contractrisk-m3` en checkout separado `repo-m3`, desde main verificado; 24 fichas públicas candidatas, manifiesto con fuentes/hashes y reconstrucción offline idéntica; cinco pruebas unitarias aprobadas. No hay todavía índice, gold QA humano, corrida RAG ni scorecard M3. Main y la rama experimental M2 no se modificaron.

## Fuentes y punto de partida

- Guía entregada: `STAI_M3_Asignacion_RAG_agentico.pdf`, seis páginas, documento del 7 de octubre de 2026.
- Comentarios del profesor aportados por el equipo: el juez de M2 queda sustituido por reglas; recibe la comparación de etiquetas; llega a elogiar una explicación vacía; prueba de verbosidad limitada y basada en puntajes corregidos; falta declaración de uso de IA.
- Main verificado: `5d82be9471baffb958096bd686a91124752691b5` en `vcastrop/Juan-Camilo-Ramon-Valentina-Castro`.
- La rama remota experimental de M2 fue eliminada. Su copia local contiene cambios incompletos y tiene un respaldo. No debe publicarse ni fusionarse automáticamente para iniciar M3.
- Evidencia histórica preservada: 20 gold de M2, nueve frontera, doble anotación, modelo M1 y resultados publicados. No se reemplazarán por resultados nuevos con la misma etiqueta de versión.

## Reglas de trabajo

Diagnóstico real incorporado: smoke v1 completó con SQLite alternativo, pero falló recuperación en 4/4 preguntas y coherencia de abstención en 4/4. No contar esto como calidad aprobada. Código de híbrido BM25/dense/RRF, filtro explícito de ID, reranking y guard FTS5 implementado; próxima corrida de desarrollo pendiente. El gold final permanece intacto.

Bloque RAG básico: adaptadores Chroma/embeddings/Qwen e interfaz de respuesta con explicación/citas implementados; prueba Colab de cuatro preguntas de desarrollo preparada. Trece pruebas locales aprobadas. Corrida real pendiente: no marcar indexación con modelos, calidad, latencia, compatibilidad de dependencias o evaluación final como verificadas. Las dependencias de smoke usan rangos candidatos y deben congelarse después de verificar el entorno.

Avance posterior a revisión humana: gold `m3-qa-gold-1.0` congelado con 12 preguntas; revisor y fecha tomados del documento del usuario, m3_004 corregido según aprobación condicionada. Evidencia original preservada con hash en `m3/eval/gold_v1/`. Ingestión determinista inicial: 40 chunks de 24 fichas, con offsets y fuentes. Diez pruebas locales aprobadas. Índice vectorial, inferencia real, calibración y métricas siguen pendientes. Estos avances reemplazan el estado anterior de «revisión humana pendiente» para las preguntas, pero no cierran toda la fase E ni certifican el corpus para todos los usos.

Avance adicional: borrador QA de 12 preguntas con respuesta, criterio y fuentes, incluidas dos sin respuesta y dos de cálculo; cuatro preguntas separadas para desarrollo. Archivo de revisión humana con las 24 fichas: `m3/eval/REVISION_HUMANA_QA.md`. Siete pruebas técnicas aprobadas. Revisión humana, calibración, congelación y ejecución con modelos siguen pendientes; no se marca la fase E como completa.

Una casilla solo se marca completa cuando existe el archivo o evidencia correspondiente y se ha verificado. Diferenciar siempre: diseñado, implementado, probado localmente, ejecutado con modelos reales y revisado por el equipo.

No afirmar que el RAG detecta fraude: su función propuesta es ayudar a un analista a comprender contratos y justificar alertas de insuficiencia con fuentes. Un hallazgo textual no demuestra una irregularidad. No inventar documentos, referencias, cifras, licencias, etiquetas humanas, revisiones del equipo ni resultados.

El objetivo no es garantizar mejores números, sino construir una comparación válida, explicar los cambios y reconocer los fallos. No elegir corridas por obtener mejores métricas.

## Resumen de mínimos de la guía

| Componente | Requisito | Evidencia de cierre propuesta |
|---|---|---|
| Corpus e índice | Corpus real, procedencia, tamaño y condiciones de uso; ingestión, fragmentación, embeddings y almacenamiento ejecutables | Manifiesto, muestra o descarga, script de indexación y estadísticas |
| Decisiones de recuperación | Justificar tamaño/solapamiento, embeddings y top-k con el corpus concreto | Configuración versionada y justificación |
| Baseline | RAG ingenuo conservado, top-k, prompt y generación, con abstención | Función y corrida identificadas |
| RAG avanzado | Al menos dos técnicas elegidas por diagnóstico | Fallos documentados, configuraciones y comparación medida |
| Herramienta | Al menos una, esquema, JSON tolerante y máximo de pasos | Trazas de dos casos que la requieren y uno que no |
| Eval set | Al menos diez preguntas con input, esperado y criterio; al menos dos sin respuesta en el corpus | Gold revisado y congelado |
| Comparación | Cuatro filas, mismas preguntas, harness, generador y prompt base; latencia mediana | Scorecard por versión y registros por consulta |
| RAGAS | Faithfulness, answer relevancy, context precision, context recall sobre el sistema final | Datos por pregunta, métricas y configuración del juez |
| Reporte | Diagrama, ambas tablas, efectos, costos, errores y abstención | README/reporte con enlaces a evidencia |
| IA | Declaración de herramientas usadas al construir el trabajo y revisión real del equipo | Sección Uso de IA confirmada por autores |
| Entrega | Ejecutable en Colab gratuito, sin claves pagas obligatorias | Notebook ejecutado limpio, evidencia guardada y enlace en Interactiva |

## A. Preparación segura y decisiones iniciales

- [x] Leer las seis páginas de la guía de M3.
- [x] Revisar los comentarios del profesor y relacionarlos con el código publicado de M2.
- [x] Comprobar el commit remoto de main y la existencia del respaldo de la rama experimental.
- [x] Recibir fecha y hora límite del equipo: 29/10/2026 a las 23:59 Colombia. Acceso directo a Interactiva no realizado.
- [x] Recibir e inspeccionar los materiales de sesiones 7, 8 y 10; identificar qué adaptar y qué ejemplos no copiar literalmente.
- [ ] Revisar cualquier instrucción adicional del profesor sobre herramientas, corpus o evaluación.
- [ ] Definir el alcance de preguntas y el usuario objetivo: consulta de información contractual con evidencia y límites claros.
- [x] Crear `Entrega/contractrisk-m3` desde main verificado en un checkout separado, sin mezclar cambios pendientes de M2.
- [ ] Acordar cuándo publicar esa rama. No publicar la antigua rama experimental ni modificar main directamente.
- [ ] Registrar decisiones, pendientes y responsabilidades reales del equipo.

**Cierre A:** alcance, fecha, repositorio de trabajo y decisiones de evaluación documentados.

## B. Resolver el cambio de clasificación a preguntas sin romper la comparación

La guía permite escribir preguntas nuevas cuando M1 era clasificación. Sin embargo, también pide una fila «línea base del Módulo 2 (sin RAG)» y mantener generador y prompt base. RoBERTalex clasifica, pero no responde preguntas ni produce explicaciones. Esta diferencia debe resolverse explícitamente antes de programar la tabla final.

- [ ] Mantener el benchmark histórico de 20 contratos y su scorecard como referencia separada, sin reutilizar sus cifras como resultados de preguntas nuevas.
- [x] Diseñar un benchmark de preguntas sobre el corpus real para M3, con posibilidad de abstención.
- [x] Documentar la propuesta de comparación en `m3/DECISIONES_INICIALES.md`: generador sin recuperación, RAG ingenuo, RAG avanzado y RAG avanzado con herramienta, todos con el mismo generador y prompt base. Rotulación final pendiente.
- [ ] Consultar/confirmar con el profesor cómo rotular la primera fila adaptada: no llamarla «RoBERTalex de M2» si utiliza un generador nuevo. Si requiere literalmente M2, acordar una adaptación compatible o una tabla adicional común de clasificación.
- [ ] Si se conserva una señal de RoBERTalex como parte del sistema, mantenerla igual en todas las variantes que se comparen; no añadirla solo a una fila sin declararlo.
- [ ] Establecer qué puede cambiar por fila: el contexto recuperado y la activación de la herramienta; conservar la instrucción base de respuesta y los parámetros de generación.
- [ ] Definir una interfaz común: entrada pregunta; salida respuesta, explicación, fuentes citadas, abstención, contexto recuperado y trazas de herramientas/tiempos.
- [ ] Reutilizar el núcleo y contrato de evaluación de M2 mediante un adaptador documentado. No exigir a un clasificador que genere explicaciones inexistentes.
- [ ] Versionar la corrección del harness ANTES de comparar sistemas y reevaluar todas las filas con esa misma versión.

**Cierre B:** ninguna fila mezcla métricas antiguas con reglas nuevas, ni atribuye a M2 un modelo que no se usó allí. La interpretación de la fila de baseline queda resuelta.

## C. Corregir los puntos señalados por el profesor

Núcleo candidato implementado en `judge.py`, rúbrica en [JUEZ_M3.md](JUEZ_M3.md). Nueve pruebas unitarias del juez pasan (42 en total). Casillas marcadas aquí indican implementación y prueba sintética; NO calibración ni ejecución real. Faltan revisión semántica y prueba multicaso de verbosidad antes de congelar la versión.

- [ ] Hacer que el RAG produzca su propia explicación breve, vinculada a la evidencia recuperada. La explicación del juez no sustituye la del sistema.
- [x] Eliminar el reemplazo de puntajes por «4 si acierta / 1 si falla» en la nueva evaluación.
- [x] No enviar al juez indicadores de coincidencia de etiquetas, veredictos de acierto/error ni instrucciones que restrinjan el puntaje según esos indicadores.
- [x] No mostrar al juez la confianza del clasificador como argumento de corrección.
- [x] Definir una rúbrica 1-5 que evalúe la respuesta y su explicación: sustento, pertinencia, citas y abstención adecuada. Anclar cada nivel.
- [ ] Probar que respuestas diferentes pueden recibir puntajes distintos aun cuando compartan la misma etiqueta.
- [x] No inventar una explicación cuando el sistema no la entrega; registrar explícitamente esa ausencia.
- [x] Corregir el parser con formatos inequívocos de una o dos líneas/JSON, sin aceptar puntajes múltiples, valores fuera de rango o razones ausentes.
- [x] Conservar salida original, resultado analizado, errores y todos los intentos. Nunca elegir entre intentos por obtener mejor puntuación.
- [x] Corregir la tasa de parsing para incluir TODOS los casos en el denominador; distinguir valores ausentes de ceros reales.
- [ ] Añadir pruebas con las respuestas reales que fallaron en v2.0, incluidas comas, acentos, preámbulos y contradicciones.
- [ ] Calibrar orientación y calidad del juez con ejemplos separados del conjunto final; dejar explícito si son sintéticos.
- [ ] Revisar que una respuesta de abstención justificada no sea penalizada por carecer de información inexistente.
- [ ] Revisar cualitativamente las razones del juez; un JSON válido no demuestra una evaluación correcta.
- [ ] Repetir verbosidad en varios pares con contenido equivalente y puntajes BRUTOS, incluyendo respuestas buenas, malas y abstenciones. Propuesta: al menos 12 pares.
- [ ] Comparar antes/después del control de longitud con igual contenido y orden controlado; reportar diferencias y fallos, no presumir mitigación efectiva.
- [ ] Preservar la corrida fallida v2.0 como diagnóstico, excluida del scorecard de M3.
- [ ] Añadir sección Uso de IA para construcción del proyecto, no solo una lista de los modelos que ejecuta el sistema.

**Cierre C:** la dimensión del juez depende de su evaluación real y ya no es una transformación automática de accuracy. Existen pruebas técnicas y revisión de explicaciones.

## D. Corpus real, procedencia e índice

- [x] Inventariar la fuente pública y campos disponibles: 24 fichas candidatas de SECOP II capturadas; no confundirlas con documentos contractuales completos ni afirmar que ya hay guías oficiales incorporadas.
- [ ] Decidir qué fuentes responden las preguntas seleccionadas. No asumir que una descripción corta contiene el contrato completo ni hechos ausentes.
- [x] Documentar origen, URL/identificador, fecha de captura, tipo de ficha y licencia declarada en los metadatos oficiales, dentro del snapshot y README del corpus candidato.
- [ ] No afirmar permiso de redistribución sin comprobarlo; cuando corresponda, guardar muestra permitida y script de descarga.
- [x] Guardar snapshot reproducible y hashes del corpus candidato; verificar reconstrucción offline idéntica.
- [ ] Excluir información personal innecesaria, credenciales y archivos privados no autorizados.
- [x] Implementar ingestión y limpieza sin eliminar cláusulas, cifras o identificadores relevantes.
- [x] Separar texto original y metadatos; conservar doc_id, fuente, sección/página y chunk_id para citar.
- [x] Excluir del índice las etiquetas gold, criterios, respuestas de referencia, evaluaciones y documentos de resultados. El corpus fuente que contiene los hechos sí debe ser recuperable.
- [ ] Medir longitudes y estructura de documentos; elegir tamaño y solapamiento con esa evidencia.
- [ ] Elegir embeddings adecuados al idioma/corpus y probar memoria/tiempo en T4; fijar identificador y revisión.
- [x] Implementar `ingest -> chunk -> embed -> store` usando Chroma por defecto; justificar otra base si se usa.
- [ ] Justificar top-k con preguntas de desarrollo y cobertura observada, no con una frase genérica.
- [ ] Reportar número de documentos y chunks, versiones, tiempo de indexación y almacenamiento.
- [x] Comprobar reconstrucción del índice desde cero.

**Cierre D:** índice reconstruible, corpus real trazable y tres decisiones justificadas con sus características.

## E. Eval set M3 y reglas de medición congeladas

- [x] Escribir al menos 10 preguntas gold; objetivo inicial de trabajo: 16-20 si el corpus y el tiempo lo permiten.
- [x] Incluir al menos 2 preguntas cuya respuesta realmente no está en el corpus completo, no solo fuera del top-k.
- [x] Incluir preguntas de datos concretos, interpretación sustentada, ambigüedad y búsqueda de identificadores; evitar un set solo fácil.
- [ ] Incluir al menos dos casos que requieran la herramienta y uno que no, identificados con criterio previo.
- [ ] Para cada pregunta guardar input, respuesta esperada, criterio, answerable, referencias documentales y necesidad esperada de herramienta.
- [x] Revisar las respuestas y fuentes por el equipo. Los borradores asistidos por IA no cuentan como anotación humana independiente sin revisión real.
- [ ] Separar ejemplos de desarrollo/calibración de los finales; registrar qué se ha usado para diagnosticar o ajustar.
- [ ] Congelar eval set, corpus, rúbrica y configuración antes de las corridas comparativas.
- [ ] Elegir una métrica automática apropiada a preguntas: por ejemplo, exactitud de hechos/campos verificables con normalización y evaluación de abstención. No reutilizar Macro F1 de etiquetas como si midiera toda una respuesta generativa.
- [ ] Si se usan similitud, F1 textual u otra métrica, justificar y fijar la definición; documentar límites ante paráfrasis.
- [ ] Definir dominio mediante verificación específica: respuesta sustentada en fuentes requeridas/citas trazables o abstención cuando no hay evidencia; no reducirlo a la misma regla determinista del acierto.
- [ ] Definir tratamiento de errores, respuestas vacías y casos no aplicables antes de calcular promedios.
- [ ] Asegurar que cada fila de la tabla usa todas las mismas preguntas; si se amplía el gold, repetir TODAS las variantes.

**Cierre E:** referencias verificadas y métricas congeladas; no hay cifras anticipadas.

## F. Generador sin RAG y RAG ingenuo

- [x] Seleccionar un generador instruct abierto que pueda ejecutarse en Colab gratuito y fijar revisión, semilla y parámetros.
- [ ] Congelar el prompt base de respuesta/explicación/citas/abstención para todas las variantes.
- [ ] Implementar el control sin recuperación conforme a la decisión de la fase B.
- [x] Implementar `sistema_rag(pregunta)`: búsqueda dense top-k, contexto delimitado y generación con fuentes.
- [ ] Implementar válvula de escape explícita cuando la respuesta no está en el contexto.
- [ ] Distinguir «no hay evidencia disponible» de «el contrato tiene una irregularidad».
- [ ] Registrar pregunta, respuesta, explicación, chunks, IDs citados, abstención, tokens si disponibles y latencia.
- [x] Medir al menos una corrida real del ingenuo sobre consultas de desarrollo.
- [x] Conservar el ingenuo como implementación independiente y fila de referencia; no sobrescribirlo con la versión avanzada.

**Cierre F:** baseline operativo y lista de fallos observados con fuentes recuperadas.

## G. Diagnóstico y al menos dos técnicas avanzadas

Opciones de la guía: búsqueda híbrida BM25 + dense con RRF; reranking con cross-encoder; transformación de consulta (multi-query, HyDE, step-back o descomposición).

- [x] Registrar consultas fallidas del ingenuo y clasificar: falta el chunk, mala ordenación, ambigüedad de consulta, contexto ignorado o respuesta ausente del corpus.
- [ ] Elegir dos técnicas en función de esos fallos. Hipótesis inicial, NO decisión cerrada: híbrida para términos/IDs exactos y reranking para documentos similares con distinta pertinencia.
- [x] Documentar por técnica la consulta afectada, evidencia y mecanismo esperado de mejora.
- [x] Implementar las técnicas sin cambiar simultáneamente el generador o el prompt base.
- [x] Mantener el presupuesto de contexto y top-k final comparables; declarar pools de candidatos adicionales.
- [x] Implementar `sistema_rag_avanzado(pregunta)` con la misma interfaz.
- [ ] Medir calidad y latencia de cada técnica. Preferir ablaciones: ingenuo, técnica A, técnica B y A+B.
- [x] Si no se hacen ablaciones, aportar análisis por casos y reconocer que no se aisló numéricamente el efecto individual.
- [x] Conservar degradaciones y casos no resueltos; no afirmar que toda técnica mejora.

**Cierre G:** dos técnicas integradas, motivadas por diagnóstico y con efecto observado.

## H. Capa agéntica con una herramienta útil

Implementación y 33 pruebas locales aprobadas (incluyen 14 del bloque agente). [Diseño, límites y ejecución](AGENTE_DESARROLLO.md). Las casillas de implementación no certifican decisiones correctas de Qwen: trazas reales y calidad siguen pendientes. Herramienta elegida: diferencia de valores de dos fichas, con consulta de operandos, cálculo Decimal, fuentes y errores explícitos. Notebook de desarrollo v3 preparado, aún no ejecutado en T4.

Propuesta inicial reemplazada por `diferencia_valores_contratos(id_a, id_b)`: consulta dos campos del snapshot y realiza la diferencia absoluta. El agente decide su uso; no se dispara por etiquetas del gold. Presupuesto cooperativo local de dos segundos, hasta tres decisiones y una respuesta final; llamadas repetidas bloqueadas.

- [x] Elegir una herramienta que resuelva una necesidad observada; no añadir una llamada ornamental.
- [x] Definir nombre, descripción, parámetros, tipos, valores admitidos y esquema de retorno.
- [x] Hacer que el modelo pueda solicitarla o responder sin usarla; registrar la decisión real.
- [x] Implementar parseo JSON tolerante pero no ambiguo; rechazar nombres desconocidos y argumentos fuera de esquema.
- [x] Establecer máximo de pasos y reintentos de reparación; propuesta inicial: tres pasos, a validar por tarea.
- [x] Manejar ID inexistente, retorno vacío, timeout y error sin inventar datos.
- [x] Limitar herramientas a operaciones permitidas y de lectura; no ejecutar código, rutas o URLs arbitrarias propuestos por el modelo.
- [x] Tratar instrucciones dentro del corpus/resultados de herramientas como datos, no como órdenes del sistema.
- [x] Mantener la instrucción base de respuesta; documentar por separado el controlador agéntico y sus prompts.
- [ ] Mostrar dos consultas reales que requieren y activan la herramienta, con argumentos/resultados, y una que no la requiere.
- [ ] Medir llamadas innecesarias, omisiones y latencia adicional; no ocultar que el agente pueda no mejorar.

**Cierre H:** herramienta ejecutada por el flujo del agente, trazas verificables y bucles acotados.

## I. Tabla evolutiva y latencia

- [ ] Ejecutar las cuatro variantes sobre el mismo eval set y versión del harness: control sin RAG acordado, ingenuo, avanzado y final con herramienta.
- [ ] Medir tiempo por consulta con la misma definición: de entrada a respuesta final, incluyendo recuperación, reranking y herramienta.
- [ ] Excluir del tiempo de respuesta el juez de evaluación; medirlo aparte si se reporta costo total de experimentación.
- [ ] Reportar carga/indexación y calentamiento por separado; mantener una política idéntica de caché entre variantes.
- [ ] Mantener hardware y condiciones comparables; registrar cambios de sesión/hardware y no atribuirlos a una técnica.
- [ ] Guardar todos los casos, errores, latencias individuales y mediana por variante. No excluir silenciosamente consultas fallidas.
- [ ] Exportar `scorecard_m3.csv` y predicciones/trazas individuales con versión y fecha.
- [ ] Comparar contra resultados recalculados, no contra el 3,4 histórico del juez ajustado de M2.
- [ ] Registrar tiempo adicional y, si se mide, memoria/tokens; no inventar costos monetarios de APIs que no se usaron.

**Cierre I:** cuatro filas completas y comparables, con tres dimensiones y latencia mediana.

## J. RAGAS

- [ ] Elegir y documentar la implementación: laboratorio de sesión 10 o librería `ragas` con LLM local. Si se usa el laboratorio, obtener su material y no suponer su contenido.
- [ ] Verificar las definiciones/API de la versión elegida antes de implementar. No llamar RAGAS a cuatro métricas sustitutas arbitrarias.
- [ ] Identificar y fijar modelos del evaluador y embeddings; no requerir claves pagas.
- [ ] Preparar por caso pregunta, respuesta final, contextos efectivamente entregados al generador y referencia.
- [ ] Calcular faithfulness del sistema final: sustento de afirmaciones en evidencia disponible.
- [ ] Calcular answer relevancy del sistema final: relación entre respuesta y pregunta.
- [ ] Calcular context precision del sistema final: pertinencia de los contextos recuperados.
- [ ] Calcular context recall del sistema final: cobertura de información necesaria de la referencia.
- [ ] Idealmente calcular también las cuatro métricas del ingenuo para localizar mejoras.
- [ ] Incorporar de forma trazable el resultado de la herramienta si se usó como evidencia al generar; distinguirlo de los chunks del retriever.
- [ ] Definir qué métricas son aplicables a preguntas no respondibles y contextos vacíos; registrar N/A con denominadores, no asignar 1 o 0 por conveniencia.
- [ ] Guardar salidas originales, parseos, fallos y número de casos válidos por métrica; revisar muestras de juicios.
- [ ] Exportar `ragas_m3.csv` y detalle por consulta, junto con configuración del evaluador.

**Cierre J:** cuatro métricas reales, auditables y con limitaciones explicadas; no basta una tabla con encabezados.

## K. Pruebas y ejecución reproducible

- [ ] Pruebas unitarias de carga/chunking/IDs, recuperación, RRF o técnica elegida, límites de contexto, esquema de salida y citas.
- [ ] Pruebas de parser ambiguo, duplicado, fuera de rango y ausencia de respuesta.
- [ ] Pruebas del denominador de métricas con cero, algunos y todos los casos fallidos.
- [ ] Pruebas de herramienta: llamada válida, inválida, innecesaria, timeout y máximo de pasos.
- [ ] Verificar que ninguna parte del gold o resultados se incorpora al índice o a la entrada del sistema.
- [ ] Notebook con pasos ordenados: requisitos, corpus, índice, pruebas, sistemas, evaluación, exportación.
- [ ] Fijar revisiones de modelos y versiones compatibles de dependencias; registrar versiones efectivas, semillas y hashes.
- [ ] Ejecutar en sesión nueva de Colab T4 de principio a fin, sin rutas de Windows ni claves pagas obligatorias.
- [ ] Verificar memoria descargando/cargando modelos por fases si es necesario.
- [ ] Reconstruir el índice desde cero y repetir una verificación de reproducción; no confundir éxito unitario con inferencia real validada.
- [ ] Conservar notebook con salidas y ZIP completo; comparar métricas recalculadas desde detalle con las tablas exportadas.

**Cierre K:** otra persona tiene instrucciones y artefactos suficientes para ejecutar y auditar; variaciones esperables quedan declaradas.

## L. Reporte, autoría y entrega

- [ ] Abrir README con qué hace ContractRisk M3, para quién y qué es una buena respuesta.
- [ ] Incorporar un diagrama desde documento hasta respuesta, marcando técnicas y herramienta.
- [ ] Incluir corpus/fuentes/condiciones de uso, decisiones de indexación, interfaz y ejemplos.
- [ ] Publicar tabla evolutiva y tabla RAGAS, enlazadas a archivos por consulta.
- [ ] Explicar qué técnica movió qué métrica y en qué preguntas; separar evidencia de hipótesis.
- [ ] Explicar la latencia añadida por técnica/agente y su utilidad para el analista.
- [ ] Distinguir fallos de recuperación, generación, herramientas y evaluación; no atribuir toda diferencia a un único componente sin evidencia.
- [ ] Analizar por separado las preguntas sin respuesta: abstención, invención o respuesta parcial.
- [ ] Documentar limitaciones y próximos pasos; no afirmar detección de corrupción ni autonomía operativa.
- [ ] Añadir «Uso de IA»: herramientas usadas para código, planificación, redacción, depuración y análisis; identificar qué revisó/cambió realmente el equipo y qué sigue pendiente.
- [ ] Declarar retroactivamente la asistencia de IA en M1/M2 de manera veraz, sin alterar fechas o simular autoría humana de material generado.
- [ ] Revisar citas, licencias, secretos, datos privados, archivos temporales y enlaces.
- [ ] Contrastar los seis criterios de rúbrica: corpus 10, técnicas 25, agente 15, harness 20, RAGAS 15, análisis 15.
- [ ] Abrir PR de M3; revisar diferencias y pruebas antes de autorizar merge a main.
- [ ] Entregar el enlace en EAFIT Interactiva y conservar comprobante. La fecha válida de retraso se basa en pushes; no cambiar fechas para aparentar una entrega anterior.
- [ ] Preparar explicación oral: ambos integrantes deben poder explicar arquitectura, métricas, decisiones y errores.

**Cierre L:** evidencia publicada y coherente, declaración de IA confirmada, revisión final y envío real. Ningún documento debe decir «completo» antes de estos cierres.

## Estructura propuesta (implementación parcial iniciada)

```text
m3/
  README.md
  CHECKLIST.md
  config/                 # modelos, revisiones, prompts y parámetros congelados
  corpus/                 # manifiesto, muestra permitida y script de descarga
  indexing/               # ingestión, fragmentación e índice
  systems/                # control sin RAG, ingenuo, avanzado y agente
  tools/                  # esquemas y funciones permitidas
  evaluation/             # adaptación del harness y RAGAS
  eval/                   # gold final, separado de corpus e índice
  calibration/            # ejemplos de desarrollo del evaluador
  tests/
  results/                # corridas identificadas y tablas derivadas
  evidence/               # diagnósticos, trazas, fuentes y revisión humana
  ContractRisk_M3_Colab.ipynb
```

## Información que debe confirmar el equipo

1. Fecha recibida: 29/10/2026 23:59 Colombia. Confirmar solo si Interactiva establece alguna condición adicional.
2. Materiales de las sesiones 7, 8 y 10 recibidos. S10 incluye implementación didáctica propia de RAGAS; no confundirla con la librería.
3. Corpus de 24 fichas utilizado en desarrollo; conservar sus límites: no contiene contratos completos.
4. Revisión humana del gold recibida y congelada; pendiente revisión de respuestas y juicios finales.
5. Interpretación del baseline sin RAG al pasar de clasificación a preguntas, conforme a fase B.
6. Aportes humanos reales para la declaración de IA. No se completarán por suposición.

## Próximo bloque de trabajo

1. Reforzar interpretación de campos y abstención mediante desarrollo, sin ajustar contra el gold.
2. Ejecutar el desarrollo v3 en T4 y revisar llamadas útiles, decisiones sin llamada y abstención. Implementación, parser y pruebas locales ya disponibles.
3. Implementar/calibrar juez independiente, dominio y RAGAS, sin transformar accuracy en puntuaciones del juez.
4. Congelar configuración y evaluar cuatro variantes con el mismo gold, generador y prompt base.
5. Completar reporte, declaración de IA y revisión antes de publicar/mergear. Confirmar rotulación del baseline adaptado.
