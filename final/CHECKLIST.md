# ContractRisk — plan y checklist de entrega final

Plan preparado el 15/11/2026 tras leer las seis páginas de la guía `STAI_Final_Asignacion_Proyecto_integrador (1).pdf` y consultar GitHub. Estado remoto: main en `afe471739a3d9192ffb32fbb78158d473dd0d619`; M1–M3 presentes, sin carpetas M4 ni final publicadas. Esto no descarta trabajo local del equipo no compartido.

Este archivo es un plan operativo, no promesa de nota. Ya está incorporado en `final/CHECKLIST.md` en la rama `Entrega/contractrisk-final`; las fechas y responsables de ejecuciones se completarán con evidencia real. No se modifica main ni se reescriben entregas anteriores.

## Fechas y reglas de la guía

- Repositorio y reporte: jueves 19/11/2026 a las 23:59. Confirmar la zona horaria publicada en Interactiva; planificación del equipo en Bogotá.
- Sustentación individual: a más tardar lunes 23/11/2026. El equipo debe acordar fecha, hora y modalidad con anticipación.
- Presentación: máximo 10 minutos, después preguntas; ambos integrantes deben explicar cualquier parte.
- Entrega: un enlace al repositorio por equipo en Interactiva; portada con URL pública de demo y proyecto W&B.
- Archivos nuevos en `final/`; conservar módulos anteriores.
- Presentación y diapositivas forman parte de la entrega, en `final/` o enlazadas.
- M4 fue opcional como entrega separada, pero el componente visual funcionando se espera en el sistema final. Su ausencia debe declararse y afecta integración/solidez; no marcar como cumplido si falta.
- Eficiencia: técnica sobre un componente; umbral de pérdida aceptable escrito antes de medir; antes/después en misma máquina, mismo gold y mismo harness; p50, p95 y memoria o tamaño.
- Observabilidad: health check, JSON por petición sin datos personales y peticiones reales del despliegue en W&B con latencia y al menos una métrica de uso.
- CI sobre 3–5 casos y video de respaldo son opcional valorado y recomendación, respectivamente, no requisitos obligatorios equivalentes.

## Arquitectura propuesta, pendiente de validación

Usuario analista/auditor -> interfaz pública -> entrada textual o imagen de ficha -> extracción visual con incertidumbre y fuente -> clasificación de suficiencia M1 cuando corresponda -> RAG M3 y herramienta numérica -> validación/citas/abstención -> respuesta revisable por persona.

El componente M1 no es detector de fraude. Su salida informa suficiencia descriptiva y no debe bloquear automáticamente consultas ni alimentar al juez como prueba de corrección. Las imágenes tampoco permiten concluir irregularidad. La visión debe cambiar efectivamente el procesamiento del sistema: un cargador de imágenes sin extracción/interpretación no cumple ese propósito.

Hipótesis de visión mínima: captura de una ficha contractual, OCR y campos estructurados enlazados con texto/ID verificado. Conservar el texto extraído y su procedencia; ante ilegibilidad o discrepancia, pedir aclaración o abstenerse. No crear datos de un contrato inexistente. Confirmar que el patrón corresponde a lo trabajado en M4/materiales del curso; no atribuirlo a una sesión sin comprobarlo.

La técnica de eficiencia y el hardware de publicación se eligen tras perfilar y probar memoria real. Cuantizar el generador es candidato, no decisión demostrada. No asumir que una implementación de cuantización para GPU corre en CPU ni que Colab proporciona una URL persistente de entrega.

## Fase 0 — insumos, seguridad y congelación del punto de partida

- [x] Leer la guía completa, incluidas rúbrica, mínimos, uso de IA y sustentación.
- [x] Consultar main y las ramas remotas sin modificarlas.
- [ ] Recibir cualquier trabajo de M4/M5 no publicado y comentarios adicionales relevantes.
- [ ] Recibir los materiales/labs de sesiones 13 y 15 y, si existen, los de visión e invarianza de M4.
- [x] Confirmar disponibilidad de Colab GPU para comparar antes/después: usuario confirma T4 el 16/11; acceso efectivo se registrará al ejecutar.
- [ ] Confirmar cuentas/permisos de Hugging Face Spaces y W&B; presupuesto/hardware disponible, sin suponer pagos.
- [ ] Acordar responsabilidades humanas y disponibilidad de ambos integrantes.
- [x] Crear rama `Entrega/contractrisk-final` desde main remoto `afe4717`; entregas anteriores preservadas.
- [ ] Inventariar modelos/adaptador, licencias, paquetes, corpus y evidencias existentes.
- [x] Ejecutar pruebas heredadas: 128 pruebas M3 aprobadas el 16/11; snapshots M1–M3 preservados. No es nueva evaluación de modelos.
- [x] Abrir checklist operativo en `final/` con evidencias por casilla.

Aceptación: base identificada, sin cambios ajenos perdidos, inventario y responsables reales. No publicar claves ni materiales privados del curso.

## Fase 1 — definir el producto y desplegar un esqueleto temprano

- [ ] Confirmar usuario: analista/auditor que consulta fichas y prioriza información insuficiente para revisión humana.
- [ ] Definir una decisión y una métrica de éxito de usuario: proporción de consultas con respuesta respaldada y sin afirmaciones indebidas; alertas omitidas y abstención reportadas aparte. Congelar definición operativa.
- [ ] Definir interfaz común textual/visual y un único punto de entrada `sistema(...)` con resultado estructurado.
- [ ] Definir modos: consulta, comparación numérica, suficiencia descriptiva y consulta con imagen.
- [ ] Definir formato de citas, errores, incertidumbre y abstención.
- [ ] Crear Space mínimo y comprobar acceso público pronto, antes de terminar la optimización.
- [ ] Probar instalación y carga en el hardware elegido; medir memoria y arranque.
- [ ] Registrar la decisión si se requiere una versión reducida, con exclusiones exactas; no presentarla como idéntica al sistema completo.

Aceptación: URL accesible y flujo mínimo real. Un mock, un notebook enlazado o respuestas guardadas no sustituyen la demo de inferencia.

## Fase 2 — integrar y corregir comportamiento sin alterar evidencia histórica

- [ ] Conectar el clasificador RoBERTalex+LoRA de M1 con un caso de uso real y visible; mantener sus etiquetas y límites.
- [ ] Conectar corpus/indexación, recuperación híbrida, reranking y herramienta M3 en el mismo servicio.
- [ ] Revisar recuperación de campos completos para cálculos y respuestas; ficha correcta no equivale a evidencia completa.
- [ ] Implementar controles de respuesta sustentada: comprobar disponibilidad del dato, citas y ausencia de afirmaciones fuera del corpus.
- [ ] Tratar preguntas de cláusulas o auditorías ausentes y entradas fuera de alcance; corregir o reportar el fallo de abstención con pruebas reales.
- [ ] Incorporar extracción desde imágenes con validación de ID, montos y legibilidad.
- [ ] Evitar que instrucciones maliciosas en preguntas o imágenes se ejecuten como instrucciones de sistema.
- [ ] Mantener esquema de herramienta, tolerancia de JSON y límites de pasos, tiempo e intentos.
- [ ] Pruebas de regresión para falsos positivos de números, negaciones y acusaciones.
- [ ] Conservar resultados M3 originales; cambios nuevos llevan versión y metadata nuevas.

Aceptación: texto e imagen se procesan de punta a punta; el usuario puede ver qué dato provino de qué fuente. Una advertencia no equivale a solucionar una alucinación.

## Fase 3 — evaluación común y criterios antes de optimizar

- [ ] Diseñar ejemplos de desarrollo/calibración separados del conjunto final; documentar que el gold M3 ya fue inspeccionado históricamente.
- [ ] Definir ampliación del gold con casos textuales, imágenes, adversariales y no respondibles, sin elegir casos solo para favorecer el sistema.
- [ ] Revisar humanamente respuestas y criterios visuales, procedencia y privacidad de imágenes; marcar las imágenes generadas.
- [ ] Definir prueba de invarianza: pares equivalentes de la misma ficha con cambios no semánticos (resolución, rotación leve o formato); no asumir que borrar un monto es transformación invariante.
- [ ] Definir cómo reciben la misma entrada las líneas base sin visión; documentar limitación, no ocultar casos ni cambiar denominadores por fila.
- [ ] Elegir tamaño de muestra y repeticiones compatibles con tiempo; registrar warm-up, parámetros, caché y condiciones. p95 de muestras pequeñas es inestable: declararlo.
- [ ] Congelar gold, harness, prompts de evaluación, métricas y hashes antes de ejecutar la comparación final.
- [ ] Mantener tres dimensiones distintas; no convertir nota del juez en función del acierto.
- [ ] Corregir/validar el juez y parsers con ejemplos de calibración separados, incluido rechazo de respuestas inventadas y evaluación de afirmaciones cortas.
- [ ] Si se modifica el evaluador, recalificar todas las filas con la misma versión; las notas antiguas no se renombran como nuevas.
- [ ] Registrar calidad automática, calidad sustentada según juez, dominio, abstención, adversariales, invarianza y casos con imagen.
- [ ] Fijar por escrito la pérdida máxima de calidad y la ganancia mínima de eficiencia aceptables antes de medir. Umbrales numéricos a acordar con el equipo, no inventar como exigencia de la guía.

Aceptación: protocolo versionado, sin sustitución de notas ni mezclas de métricas/hardware. Si el juez falla calibración, no usarlo como evidencia de calidad validada.

## Fase 4 — perfilado, técnica de eficiencia y medición

- [ ] Perfilar latencia y memoria por componente sobre el sistema integrado previo a optimizar; si no existe M4 anterior, declarar esta nueva base visual.
- [ ] Elegir una técnica admitida: cuantización int8/int4, destilación o LoRA/QLoRA en modelo más pequeño. LoRA histórico de M1 por sí solo no prueba una mejora nueva.
- [ ] Conservar una versión antes sin la técnica y una después; no cambiar recuperación/prompt/modelo base y atribuir todo a cuantización.
- [ ] Validar compatibilidad real de la técnica con el hardware y licencias de distribución.
- [ ] Ejecutar ambas en la misma máquina y mismo conjunto, con condiciones de medición documentadas.
- [ ] Guardar por petición calidad, latencia y componentes; medir p50/p95, memoria pico o tamaño con unidades claras.
- [ ] Repetir válvula, adversariales e invarianza sobre la versión eficiente; no inferir seguridad de una calidad media similar.
- [ ] Comparar con el umbral fijado; aceptar o rechazar la técnica de forma explícita.
- [ ] Conservar un resultado negativo si la técnica no sirvió y explicar qué versión se despliega.

Aceptación: tabla antes/después calculada desde registros, umbral previo trazable y decisión basada en evidencia. No prometer mejora antes de medir.

## Fase 5 — tabla evolutiva, ablación y análisis

- [ ] Ejecutar línea base sin RAG adaptada de M2, M3, nueva base visual M4 y final eficiente sobre el mismo eval set/harness.
- [ ] Mantener el clasificador original M1/M2 como resultado histórico aparte cuando sus métricas no sean comparables a QA; no mezclar Macro F1 de clasificación con cobertura de hechos.
- [ ] Registrar mediana y resultados del subconjunto de imagen con denominadores; todas las filas se someten al protocolo común.
- [ ] Hacer al menos una ablación medida (por ejemplo sin reranking o sin herramienta), idealmente reutilizar el antes/después como evidencia adicional sin confundir ambas preguntas.
- [ ] Analizar al menos cinco fallos reales agrupados por extracción visual, recuperación, generación, herramienta o evaluación; indicar componente y reparación propuesta.
- [ ] Reevaluar RAGAS si se comparan respuestas nuevas y se reporta su delta; no atribuir métricas M3 a la versión final.
- [ ] Guardar respuestas, contextos, imágenes/referencias permitidas, trazas, versiones y resultados por caso.

Aceptación: tablas recalculables y resultados honestos, no selección de mejores corridas. Si hay menos de cinco fallos, ampliar diagnóstico y describir selección sin fabricar errores.

## Fase 6 — producción y observabilidad

- [ ] Publicar el sistema final viable en Hugging Face Spaces, no solo un formulario.
- [ ] Mostrar advertencia de alcance y revisión humana, citas y abstención comprensibles.
- [ ] Definir límites de longitud, imagen, concurrencia y tiempo; manejar errores sin revelar secretos.
- [ ] Health check documentado que no invoque una consulta real: estado de modelos/índice, carga, versión; distinguir proceso vivo de servicio listo.
- [ ] Logging JSON por petición: hora UTC, ID aleatorio, latencia, RAG/herramienta/visión utilizados y abstención; añadir versión/error sin contenido personal.
- [ ] No guardar por defecto preguntas, imágenes, OCR ni identificadores personales en logs, repo o W&B; informar al usuario de procesamiento y retención.
- [ ] Integrar W&B con latencia por petición real del despliegue y al menos una métrica de uso (por ejemplo proporción de herramienta, visión o abstención).
- [ ] Configurar secretos fuera de Git y documentar modo sin W&B/secreto, sin romper la consulta; la evidencia de W&B sigue siendo obligatoria para el cierre.
- [ ] Verificar acceso del evaluador al proyecto W&B o capturas legibles sin exponer información sensible.
- [ ] Probar arranque frío, petición textual, visual, cálculo, abstención y error de entrada desde URL pública.
- [ ] Registrar diferencias de hardware entre benchmarking y demo; no comparar sus latencias como antes/después.
- [ ] Opcional: GitHub Action sobre 3–5 casos con umbral claro; no sustituye pruebas de modelos reales.

Aceptación: URL pública verificable, health check utilizable, eventos reales visibles en W&B y logs sanitizados. Sin claves de pago obligatorias.

## Fase 7 — reporte, portada y presentación

- [ ] `final/reporte.md`: problema, usuario, decisión y métrica de éxito de usuario.
- [ ] Diagrama desde pregunta/imagen hasta respuesta con procedencia M1–M5 de cada componente.
- [ ] Decisiones de modelo, recuperación, visión y eficiencia, cada una con alternativa descartada y motivo.
- [ ] Tabla evolutiva y tabla antes/después con condiciones, p50/p95 y memoria/tamaño.
- [ ] Ablación, cinco errores, límites y conducta cuando no sabe.
- [ ] Ética en máximo media página: a quién falla más (medido o sospechado), datos/retención/conocimiento del usuario y daño de un error con mitigaciones concretas.
- [ ] Una línea por integrante: trabajo humano realmente hecho; sección corta de uso de IA incluyendo código, análisis, texto y diapositivas.
- [ ] README raíz como portada: frase sencilla, URL demo, W&B, ejecución breve e índice a módulos/reporte.
- [ ] Scripts de eficiencia, despliegue o enlace a repo del Space, configuraciones y evidencias en `final/`.
- [ ] Diapositivas claras para máximo 10 minutos: problema, dibujo, demo fácil/difícil/adversarial, comparaciones, eficiencia y peor fallo.
- [ ] Acordar fecha/hora/modalidad de sustentación antes del 23/11; ambos preparan explicaciones individuales.
- [ ] Recomendado: video corto de respaldo, con versión y resultados reales.

## Fase 8 — cierre verificable

- [ ] Clonar desde cero; ejecutar pruebas, reconstruir índice y seguir portada sin rutas locales.
- [ ] Recalcular tablas desde evidencia; no prometer identidad universal entre entornos por fijar semilla.
- [ ] Revisar privacidad, licencias, secretos, enlaces y acceso público de demo/W&B.
- [ ] Revisar rúbrica de 40 puntos: problema 4; solidez 8; evaluación 7; integración 4; presentación 7; producción 5; límites 3; ética 2.
- [ ] Publicar commits claros y abrir PR; fusionar solo con aprobación del equipo.
- [ ] Entregar enlace en Interactiva antes del plazo y conservar comprobante real.
- [ ] Comprobar URL el día de la sustentación; verificar acceso o video de respaldo.

## Secuencia temporal propuesta (no constituye evidencia de ejecución)

| Fecha, Bogotá | Prioridad |
|---|---|
| 15/11 | Insumos, rama, alcance, inventario, primera prueba de despliegue y protocolo de evaluación |
| 16/11 | Integración M1+M3+visión, abstención y casos adversariales; revisión humana visual |
| 17/11 | Congelar protocolo; perfilado, técnica eficiente y comparación controlada |
| 18/11 | Tabla evolutiva/ablación, W&B, pruebas públicas y borrador del reporte/presentación |
| 19/11 | Reproducción, auditoría final, PR, publicación y entrega con margen antes de 23:59 |
| Hasta 23/11 | Sustentación acordada y demo funcionando |

El calendario es ajustado y depende de GPU, cuentas y revisión humana. Si una dependencia bloquea, priorizar un sistema reducido real y documentado sobre prometer funciones no ejecutadas; la ausencia visual o de W&B no se marca como cumplida.

## Confirmaciones recibidas el 16/11/2026

- El equipo confirma que no hay desarrollo M4/M5 fuera de GitHub.
- Colab con GPU T4 sigue disponible para ejecuciones.
- Hugging Face y W&B: cuentas todavía no creadas; registro/validación de identidad pendiente por el titular.
- Recibidos S11 visión, S12 difusión y S13 integración visual (PPTX y notebooks resueltos). La presentación S13 cubre sesiones 13/14 y anticipa S15; no equivale al laboratorio de cuantización/despliegue/W&B de S15.
- Patrón visual propuesto pendiente de decisión del equipo: imagen/captura de ficha contractual como entrada, extracción de campos y conexión real con el sistema M3. No se ha implementado ni evaluado todavía.
- Referencias nuevas para el plan: al menos cinco casos visuales; evaluar respuesta final y extracción por separado; campos ausentes explícitos; calibrar el juez y medir sus falsos positivos/negativos. El notebook de integración incluye un sustituto de M3 y cifras de ejemplo, que no se usarán como sistema ni evidencia de ContractRisk.
- Las fechas y ponderaciones antiguas de M4 presentes en los materiales no reemplazan las instrucciones de la guía final.
- Riesgo de despliegue identificado al consultar documentación oficial de Hugging Face el 16/11: creación de Spaces con cómputo sujeta a plan, con excepción ZeroGPU para cuentas gratuitas elegibles (correo verificado y antigüedad indicada de más de 30 días). Una cuenta nueva puede no ser elegible antes del plazo. Comprobar en la cuenta real y, si bloquea, solicitar acceso institucional/excepción académica o acordar alternativa; no activar pagos ni dar por resuelto mediante un Space estático sin inferencia.

## Información que debe aportar el equipo ahora

### Decisiones posteriores confirmadas por el usuario

- No se encuentra material de S15: continuar con la guía final y documentación oficial, sin atribuir decisiones a material no recibido.
- Aprobado el patrón de visión como entrada mediante capturas de fichas contractuales.
- Cuentas de Hugging Face y W&B creadas; el usuario dispone de API key de W&B. No se ha recibido ni debe guardarse su valor en el repositorio o en la conversación.
- Pendientes de infraestructura: nombres de usuario, entidad/proyecto W&B y opciones de creación de Space disponibles en la cuenta real. No se ha comprobado todavía elegibilidad, hardware ni despliegue.
- Capturas aportadas después: propietario Hugging Face `jcramonp`; creación permite Static y muestra Gradio/Docker bloqueados con etiqueta Paid. No hay Space dinámico creado ni permiso para comprar un plan. Una página estática sola no cumple inferencia del sistema.
- W&B confirmado visualmente: usuario `jcramonp`, equipo candidato a entity `jcramonp-eanit`, organización `jcramonp-eanit-org` (Academic). Proyecto propuesto `contractrisk-final`. Existe una clave activa administrada en la organización; no se conoce su valor ni se ha comprobado autenticación/permiso de escritura. Validar en primera ejecución segura, no confundir organización con entity.
- El usuario confirma haber configurado `WANDB_API_KEY` en secretos de Colab; autenticación y escritura todavía no probadas.
- Nueva cuenta Hugging Face mostrada en capturas: propietario `Juanoff`, Gradio y ZeroGPU Free seleccionables. Se prioriza esta opción para probar el despliegue pedido por la guía; Modal queda como respaldo, no como decisión de migración. Todavía no se ha creado ni probado el Space ni verificado carga, cuotas o compatibilidad del pipeline.

1. Trabajo/materiales M4/M5 no publicados y sesiones 13/15; si no existen, indicarlo.
2. Usuario de Hugging Face y permisos para crear un Space; acceso a W&B y disponibilidad de Colab T4. No enviar tokens en mensajes.
3. Disponibilidad de Juan y Valentina para revisión de ejemplos, ejecuciones y sustentación.
4. Confirmación de la propuesta de visión con capturas de fichas públicas o imágenes ya revisadas sin datos personales.
5. Cualquier instrucción adicional de Interactiva y acuerdo de horario de sustentación.
