# Archivo histórico — no usar como estado vigente

Conservado al integrar bc93baa. El estado vigente está en CHECKLIST.md y RUTA_ENTREGA.md.

# ContractRisk Colombia: ruta de trabajo M3 y correcciones de M2

Plan inicial: 28 de octubre de 2026. Actualizado: 29 de octubre de 2026, tras auditar integración v5 y calibración en T4.

## Estado vigente — corrida final sobre el gold ejecutada y auditada (29/10/2026)

**Actualización posterior de integración:** [CIERRE_AUDITADO.md](CIERRE_AUDITADO.md) es la guía vigente. Se integró el bundle sin modificar main. 113 pruebas locales aprobadas.

- [x] Conservar la corrida final original y las auditorías de desarrollo v6.
- [x] Corregir y probar reglas deterministas de cifras, negaciones explícitas y acusación insinuada sin retocar gold ni respuestas.
- [x] Recalcular las 72 respuestas con reglas 1.1 y registrar las dos diferencias: dominio avanzado 3/12 y final 4/12.
- [x] Reparar divisor de afirmaciones de RAGAS y manejo de veredictos ambiguos/ausentes en módulo separado, con regresiones.
- [x] Preparar reevaluación RAGAS sobre respuestas congeladas, sin repetir generación.
- [ ] Ejecutar esa reevaluación en T4 y auditar nuevos juicios. El código probado localmente no prueba calidad semántica.
- [ ] Confirmar contribuciones humanas de Uso de IA, revisar publicación y PR.

Las tablas finales 1.0 que siguen se conservan como evidencia histórica; su falso pase de dominio no es el resultado auditado actual. La abstención y la fiabilidad del juez siguen siendo limitaciones abiertas.

Evidencia: [README de M3 con tablas y lectura honesta](README.md#resultados), [auditoría de la corrida final](results/final_m3/ANALISIS.md), `results/final_m3/scorecard_m3.csv` y `ragas_m3.csv`.

- [x] Harness `m3-harness-1.0`: tres dimensiones, latencia mediana, N/A y denominadores fijados antes de correr el gold (`harness_m3.py`).
- [x] RAGAS del laboratorio S10, con las cuatro métricas y juez Qwen2.5-3B local, sobre ingenuo, avanzado y final (`ragas_m3.py`).
- [x] Cuatro filas más dos ablaciones sobre las 12 preguntas gold, con el mismo generador, prompt y harness; 72 respuestas y 72 juicios válidos.
- [x] Herramienta usada en los 2 cálculos y no usada en 9/10 preguntas no aritméticas; la llamada innecesaria de m3_009 queda reportada.
- [x] Reporte con frase sencilla, diagrama, decisiones, tablas, lectura de las cuatro preguntas y Uso de IA.
- [ ] El equipo confirma en Uso de IA qué revisó o modificó personalmente.
- [ ] Publicar la rama (push) y entregar el enlace en Interactiva; los autores conservan el comprobante.
- [x] Revisión del equipo y del profesor incorporada: `m3-harness-1.1` corrige los defectos deterministas y recalifica las respuestas guardadas sin regenerarlas (`results/final_m3_rescore_v1_1/`). El reporte deja de presentar la dim. 1 como accuracy y la dim. 3 como aptitud, y separa localización de documento de recuperación del dato.
- [x] RAGAS 1.1 implementado (segmentación corregida; variante exacta del laboratorio y adaptación por separado) con su notebook.
- [x] RAGAS 1.1 ejecutado en Colab T4 y conservado junto a 1.0 (`results/final_m3_ragas_v1_1/`). La adaptación se reproduce idéntica; la context precision del laboratorio es inútil (el juez dice «No» a todo) y el context recall del laboratorio coincide con el chequeo determinista en 28/30.
- [ ] Integrar con las evidencias v6 del equipo (no presentes en esta rama) antes del PR.
- [ ] Fallos abiertos, documentados y sin corregir: válvula 0/2 en avanzado y final (m3_012 inventa una auditoría), falso pase de dominio en m3_009, juez RAGAS 3B poco fiable a nivel de chunk y divisor de afirmaciones que parte los IDs.

Las casillas de las fases A–L siguientes son históricas. Donde contradigan este bloque, prevalece este bloque.

## Estado anterior — integración v5 auditada

**Actualización: v6 auditada, no adoptada completa.** [Evidencia](evidence/correction_v6/ANALISIS.md): mejora parcial de abstención, regresión de controlador y juez aún no fiable. 30/32 formatos válidos; 48/48 transcripciones del juez no literales. Corpus/gold no modificados. Implementado [núcleo candidato del harness QA](HARNESS_QA.md) con tests sintéticos; faltan juez aprobado, RAGAS, runner final y corrida gold. Se mantiene avance aproximado de 60%: no confundir código nuevo con evaluación cerrada.

- [x] Preservar ZIP/notebook v6 y documentar mejoras/regresiones sin adoptar automáticamente la versión más reciente.
- [x] Implementar núcleo genérico `harness(eval_set, sistema, juez)` con aislamiento de gold, errores, denominadores y latencia mediana.
- [ ] Congelar las métricas candidatas: F1 lexical no mide verdad y trazabilidad estructural no demuestra sustento semántico.
- [x] Implementar adaptación didáctica S10 de cuatro métricas RAGAS, con originales, errores nulos y N/A explícitos. [Definiciones y límites](RAGAS_METODO.md). 86 tests locales totales aprobados; NO ejecución ni validación del evaluador.
- [ ] Integrar runner/exportación, calibrar evaluador y ejecutar harness/RAGAS sobre gold después de congelar configuración.

**Siguiente bloque preparado:** [corrección candidata v6](CORRECCION_V6.md), con reproducción de contextos de desarrollo y juez que cita/contrasta la respuesta antes de puntuar. Código y pruebas locales no certifican mejora real: pendiente corrida T4 y revisión. No cambia el porcentaje por anticipar resultados; gold y evidencias v5 intactos.

- [x] Añadir regresiones de contrato para fallos v5, aislamiento de referencias, preservación de notas y reintentos solo de formato.
- [x] Preparar notebook de diagnóstico v6 y conservar v5 como comparación histórica.
- [ ] Ejecutar v6 y revisar semántica antes de congelar configuración; no marcar resuelta la abstención o calidad del juez por pasar tests.

**Avance estimado de M3: aproximadamente 60% (rango orientativo 55–65%).** Es una estimación de trabajo completado y verificado, no una nota académica, probabilidad de éxito ni porcentaje del conjunto M1+M2+M3. No se calcula contando casillas: hay tareas de tamaños distintos y antecedentes repetidos. Corpus/gold y sistemas están muy avanzados; calibración está ejecutada pero revela fallos; harness final, RAGAS, corrida gold y entrega aún tienen trabajo sustancial.

Evidencia: [auditoría v5 y originales](evidence/integration_v5/ANALISIS.md). 23 hashes de código coinciden, 62 pruebas aprobadas, notebook sin errores, resumen del juez recalculado desde detalle y coincidente.

| Bloque | Estado real |
|---|---|
| Corpus e índice; gold humano | 24 fichas, 133 chunks en v5 y 12 preguntas finales revisadas; no se ha ejecutado el gold |
| Cuatro sistemas de desarrollo | 32 respuestas válidas de formato; 31 al primer intento; no equivale a 32 respuestas correctas |
| Recuperación avanzada | Cuatro modalidades correctas; siguen fallos de cálculo sin herramienta y de abstención |
| Agente | Dos cálculos correctos y una modalidad sin herramienta demostrados; tres llamadas innecesarias rechazadas |
| Juez y sesgo | 48 juicios brutos y 12 pares antes/después auditados; mitigación sin mejora y contradicciones semánticas |
| Harness final y RAGAS | Pendientes de completar, definir/congelar métricas y ejecutar |
| Reporte y entrega | Diagnósticos preservados; tablas finales, declaración de IA, revisión y publicación pendientes |

- [x] Ejecutar integración de las cuatro variantes con mismo generador/protocolo sobre desarrollo.
- [x] Ejecutar y revisar técnicamente los 48 juicios de calibración, sin sustituir sus notas por reglas.
- [x] Registrar evidencia de dos cálculos con herramienta y una consulta respondida sin llamada.
- [x] Medir antes/después el efecto de longitud y declarar que la mitigación no mejoró la medida (0,583 a 0,833 de diferencia absoluta media).
- [ ] Resolver o delimitar explícitamente fallos de abstención y contradicciones del juez; revisión humana del equipo pendiente.
- [ ] Completar harness de tres dimensiones y RAGAS; congelar reglas antes de evaluar gold.
- [ ] Ejecutar cuatro filas sobre gold y completar reporte/reproducción/PR.

Las casillas A–L distinguen implementación, ejecución y calidad. Los apartados históricos siguientes no son pendientes actuales ni deben sumarse de nuevo al avance. Main permanece intacto.

## Historial de corridas v2–v4 y prueba de protocolo (no estado vigente)

**Última evidencia: prueba de protocolo completada.** [Análisis](evidence/protocol_probe/ANALISIS.md): candidato 3B/v5 con 6/6 formatos iniciales válidos, 5/6 controles mecánicos y 4/4 decisiones correctas. Persiste fallo de clausulado y reserva semántica en abstención de auditoría. Seleccionado solo para integración; no aprobado como sistema final.

- [x] Ejecutar y auditar las tres condiciones de la prueba sintética, incluidas explicaciones y decisiones.
- [x] Documentar elección del candidato 3B/v5 y sus limitaciones, sin ocultar regresión de 1.5B/v5.
- [ ] Integrar candidato en las cuatro variantes y validar con desarrollo real; mantener mismo modelo/protocolo por fila.
- [x] Implementar integración 3B/v5 con protocolo común y preservar trazas; 62 pruebas locales aprobadas. [Bloque de integración/calibración](INTEGRACION_V5.md). La casilla superior sigue abierta hasta validar la corrida real.
- [x] Preparar 12 pares sintéticos de calibración/verbosidad, 48 juicios antes/después, sin comunicar expectativas al juez ni ajustar sus notas. Pendiente ejecución y revisión de razones.
- [ ] Calibrar juez independiente y verbosidad multicaso; completar dominio/RAGAS antes de evaluación final.

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
- [x] Establecer qué puede cambiar por fila: el contexto recuperado y la activación de la herramienta; conservar la instrucción base de respuesta y los parámetros de generación. Integración v5; congelación final pendiente.
- [x] Definir una interfaz común: entrada pregunta; salida respuesta, explicación, fuentes citadas, abstención, contexto recuperado y trazas de herramientas/tiempos. Implementada y ejecutada en v5.
- [ ] Reutilizar el núcleo y contrato de evaluación de M2 mediante un adaptador documentado. No exigir a un clasificador que genere explicaciones inexistentes.
- [ ] Versionar la corrección del harness ANTES de comparar sistemas y reevaluar todas las filas con esa misma versión.

**Cierre B:** ninguna fila mezcla métricas antiguas con reglas nuevas, ni atribuye a M2 un modelo que no se usó allí. La interpretación de la fila de baseline queda resuelta.

## C. Corregir los puntos señalados por el profesor

Núcleo en `judge.py`, rúbrica en [JUEZ_M3.md](JUEZ_M3.md). Integración v5 ejecutó 48 juicios reales sobre 12 pares sintéticos. Revisión técnica completada; se detectan contradicciones y mitigación sin mejora. No está aprobada la calidad del juez ni congelada su configuración final. Revisión humana pendiente.

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
- [x] Revisar cualitativamente las razones del juez; un JSON válido no demuestra una evaluación correcta. Revisión técnica asistida de 48 razones documentada en auditoría v5; revisión humana adicional pendiente.
- [x] Repetir verbosidad en varios pares con contenido equivalente y puntajes BRUTOS, incluyendo respuestas buenas, malas y abstenciones: 12 pares sintéticos, 48 juicios.
- [x] Comparar antes/después del control de longitud con igual contenido y orden controlado; reportar diferencias y fallos, no presumir mitigación efectiva. La medida empeoró en v5.
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
- [x] Elegir embeddings adecuados al idioma/corpus y probar memoria/tiempo en T4; fijar identificador y revisión. Multilingual MiniLM ejecutado; no confundir compatibilidad con buena recuperación densa: fallos documentados.
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
- [x] Separar ejemplos de desarrollo/calibración de los finales; registrar qué se ha usado para diagnosticar o ajustar. Ocho consultas de desarrollo y doce casos sintéticos del juez; gold final aún no ejecutado.
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
- [x] Implementar el control sin recuperación conforme a la decisión de la fase B. Control generativo Qwen, NO RoBERTalex; confirmación de rotulación académica pendiente.
- [x] Implementar `sistema_rag(pregunta)`: búsqueda dense top-k, contexto delimitado y generación con fuentes.
- [ ] Implementar válvula de escape explícita cuando la respuesta no está en el contexto.
- [ ] Distinguir «no hay evidencia disponible» de «el contrato tiene una irregularidad».
- [x] Registrar pregunta, respuesta, explicación, chunks, IDs citados, abstención, tokens si disponibles y latencia. Evidencia de desarrollo v5 preservada.
- [x] Medir al menos una corrida real del ingenuo sobre consultas de desarrollo.
- [x] Conservar el ingenuo como implementación independiente y fila de referencia; no sobrescribirlo con la versión avanzada.

**Cierre F:** baseline operativo y lista de fallos observados con fuentes recuperadas.

## G. Diagnóstico y al menos dos técnicas avanzadas

Opciones de la guía: búsqueda híbrida BM25 + dense con RRF; reranking con cross-encoder; transformación de consulta (multi-query, HyDE, step-back o descomposición).

- [x] Registrar consultas fallidas del ingenuo y clasificar: falta el chunk, mala ordenación, ambigüedad de consulta, contexto ignorado o respuesta ausente del corpus.
- [x] Elegir dos técnicas en función de esos fallos: híbrida BM25/dense/RRF con filtro ID y reranking. Diagnóstico y desarrollo v2–v5 preservados; no atribuir toda mejora a una sola técnica.
- [x] Documentar por técnica la consulta afectada, evidencia y mecanismo esperado de mejora.
- [x] Implementar las técnicas sin cambiar simultáneamente el generador o el prompt base.
- [x] Mantener el presupuesto de contexto y top-k final comparables; declarar pools de candidatos adicionales.
- [x] Implementar `sistema_rag_avanzado(pregunta)` con la misma interfaz.
- [ ] Medir calidad y latencia de cada técnica. Preferir ablaciones: ingenuo, técnica A, técnica B y A+B.
- [x] Si no se hacen ablaciones, aportar análisis por casos y reconocer que no se aisló numéricamente el efecto individual.
- [x] Conservar degradaciones y casos no resueltos; no afirmar que toda técnica mejora.

**Cierre G:** dos técnicas integradas, motivadas por diagnóstico y con efecto observado.

## H. Capa agéntica con una herramienta útil

Implementación y trazas reales v5 auditadas; suite total de 62 pruebas aprobadas en la corrida. [Diseño](AGENTE_DESARROLLO.md) y [evidencia actual](evidence/integration_v5/ANALISIS.md). La herramienta obtiene valores del snapshot, calcula con Decimal y conserva fuentes. Demostrados dos cálculos correctos y una consulta sin llamada; persisten tres llamadas innecesarias rechazadas y fallos de abstención. No afirmar autonomía operativa.

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
- [x] Mostrar dos consultas reales que requieren y activan la herramienta, con argumentos/resultados, y una que no la requiere. V5: índices de desarrollo 4, 5 y 2, respectivamente.
- [x] Medir llamadas innecesarias, omisiones y latencia adicional; no ocultar que el agente pueda no mejorar. V5: 3/6 consultas no aritméticas tienen llamada innecesaria rechazada; 0/2 cálculos omitidos; mediana 9,891 s frente a 7,574 s avanzado. Pendiente medición final gold.

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

- [x] Elegir y documentar la implementación: adaptación didáctica S10, no librería oficial. Véase RAGAS_METODO.md; pendiente corrida real.
- [x] Verificar las definiciones/API de la versión elegida antes de implementar. Leído bloque Lab C del laboratorio S10; variantes y diferencias declaradas.
- [ ] Identificar y fijar modelos del evaluador y embeddings; no requerir claves pagas.
- [ ] Preparar por caso pregunta, respuesta final, contextos efectivamente entregados al generador y referencia.
- [ ] Calcular faithfulness del sistema final: sustento de afirmaciones en evidencia disponible.
- [ ] Calcular answer relevancy del sistema final: relación entre respuesta y pregunta.
- [ ] Calcular context precision del sistema final: pertinencia de los contextos recuperados.
- [ ] Calcular context recall del sistema final: cobertura de información necesaria de la referencia.
- [ ] Idealmente calcular también las cuatro métricas del ingenuo para localizar mejoras.
- [ ] Incorporar de forma trazable el resultado de la herramienta si se usó como evidencia al generar; distinguirlo de los chunks del retriever.
- [x] Definir qué métricas son aplicables a preguntas no respondibles y contextos vacíos; registrar N/A con denominadores. Reglas candidatas documentadas en RAGAS_METODO.md, pendientes congelación conjunta.
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
2. Añadir regresiones de los fallos v5 (cifras, abstención y confusión respuesta/evidencia del juez); probar ajustes acotados sobre desarrollo/calibración. No repetir v3 ni tocar el gold para ajustar prompts.
3. Completar/calibrar juez, métricas automática/de dominio y RAGAS, sin transformar accuracy en puntuaciones del juez. La prueba multicaso ya se ejecutó: documentar su resultado negativo y verificar cualquier nueva mitigación.
4. Congelar configuración y evaluar cuatro variantes con el mismo gold, generador y prompt base.
5. Completar reporte, declaración de IA y revisión antes de publicar/mergear. Confirmar rotulación del baseline adaptado.

