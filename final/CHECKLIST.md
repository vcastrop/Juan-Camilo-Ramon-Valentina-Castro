# ContractRisk — plan y checklist de entrega final

## Estado vigente — dominio de los cinco perfiles cerrado

**Ventana de cierre:** [ruta priorizada de tres horas](CIERRE_TRES_HORAS.md).
Dominio histórico cerrado no significa dominio del nuevo OCR ni servicio público listo.

### Ruta actual: integración20 recibida; cierre21 de calidad preparado

- [x] Recibir y validar [revisión humana visual21](evidence/visual21_received/RECEPCION.md): diez decisiones completas, fuentes sin editar; salvedades conservadas.
- [x] Conservar [detención21](evidence/evaluation21_setup_failed/ANALISIS.md) previa a API y corregir verificación CRLF/LF sin modificar contenido ni plan.
- [x] Ejecutar ocho notas API: [cierre21](evidence/evaluation21_completed/ANALISIS.md), 22 notas completas y USD5,9179725 estimados/reservados, sin alterar 167 asientos previos.

- [x] Conservar y auditar [20](evidence/integration20_completed/ANALISIS.md): 22+16 casos, 467 pruebas, sin errores técnicos.
- [x] Verificar 14 paquetes idénticos para transferir notas, sin cambiar las bajas; doce revisiones textuales transferibles.
- [x] Preparar evaluación de ocho paquetes cambiados bajo el registro USD7 existente y revisión humana nueva de diez imágenes.
- [x] Recibir [evaluación21](EVALUACION_21.md) completa y auditar razones del juez; revisión humana ya recibida.
- [x] Recalcular dominio OCR20 con reglas originales: 18/22 (8/12 texto, 10/10 imagen), media juez 4,4545; cuatro fallos textuales preservados.
- [x] Preparar [paquete OCR22](evidence/space_ocr22_prepared/ANALISIS.md) separado, cinco archivos y tres imágenes smoke fuera del payload; salud de cuatro modelos + OCR, sin juez ni claves.
- [ ] Subir y verificar [despliegue OCR22](DESPLIEGUE_OCR_22.md)/W&B públicamente; las pruebas locales simuladas no completan este punto.
  - Primer build HF correcto pero startup incompleto; [diagnóstico seguro preparado](evidence/space_ocr22_prepared/ARRANQUE_FALLIDO.md). No se declara servicio listo ni causa raíz confirmada.
  - Diagnóstico localiza carga safetensors del adaptador M1 bajo ZeroGPU. [Corrección23](evidence/space_ocr23_cpu/ANALISIS.md) fuerza lectura CPU, preserva pesos y diagnóstico; actualización de dos archivos pendiente de verificar en HF.
  - [x] Recibir [salud23 lista](evidence/space_ocr23_cpu/SALUD_LISTA.md): cuatro modelos, OCR5.5.0 e índice listos; versión correcta. Evidencia del usuario, no consulta inferencial ni prueba externa independiente.
  - [x] Recibir [siete rutas reales](evidence/space_ocr23_cpu/SMOKE_RECIBIDO.md): QA/cálculo/tres imágenes/abstención sin fuente/M1, sin errores, con fuentes o guardas pertinentes; limitaciones preservadas.
  - [ ] Recibir salud posterior, comprobar eventos en run W&B y acceso externo; queued_check_dashboard solo confirma encolado.

### Ruta actual: OCR19 recibido; integración20 separada preparada

- [x] Conservar [OCR19](evidence/ocr19_completed/ANALISIS.md): 8/8 lecturas completas y 12/12 rutas diagnósticas, no respuestas QA.
- [x] Preparar perfil OCR20 con campos acotados y guardas, sin cargar Qwen2-VL ni editar su línea base.
- [x] Fijar evaluación del perfil nuevo en los 22 casos comunes + 16 comprobaciones separadas.
- [x] Ejecutar integración20; revisión/juez nuevos preparados, todavía sin actualizar dominio.
- [ ] Verificar luego despliegue/observabilidad reales; main y Space siguen intactos.

### Ruta actual: visual 18 rechazado; candidato OCR 19 separado

- [x] Conservar ZIP/notebook [18](evidence/visual18_completed/ANALISIS.md), verificar ocho PNG y recalcular diagnósticos.
- [x] Reconocer 0/5 legibles útiles y que dos abstenciones de controles no demostraron la detección esperada.
- [x] Preparar un candidato OCR distinto, sin alterar Qwen ni métricas previas; doce imágenes congeladas y prueba CPU sin API.
- [x] Ejecutar y revisar [OCR 19](OCR_19.md): extracción útil en la muestra, no evaluación de respuestas QA.
- [ ] Integrar/versionar y verificar controles/casos afectados antes de desplegar: perfil20 preparado, prueba real pendiente.

### Última recepción: despliegue 17 completado, diagnóstico visual 18 preparado

- [x] Conservar y verificar [ZIP/notebook 17 completados](evidence/deployment17_completed/ANALISIS.md): 441 pruebas, cinco modelos/índice, siete casos.
- [x] Comprobar M1, QA, cálculo y controles; reconocer error visual de un cero extra y falsa abstención.
- [x] Fijar ocho imágenes y expectativas diagnósticas antes de otra inferencia; modelos/prompts/guardas sin cambios.
- [x] Ejecutar y revisar una sola tanda [visual 18](VISUAL_DESPLIEGUE_18.md): utilidad visual rechazada; no repetir.
- [ ] Verificar después ZeroGPU real y telemetría de peticiones públicas; Colab no demuestra estos hitos.

**Despliegue: ruta actual [prueba 17](DESPLIEGUE_17.md).** La prueba 16 falló
instalando dependencias; se conserva [evidencia original](evidence/deployment16_failed/ANALISIS.md).
No produjo respuestas de modelos ni afecta las métricas anteriores.

- [x] Diagnosticar conflicto Gradio/Hub y conservar fallo sin presentarlo como éxito.
- [x] Fijar versiones compatibles y añadir comprobación de entorno, bloqueo y metadata de fallos tempranos.
- [x] Ejecutar y auditar el notebook **Despliegue 17** en T4: completado; límite visual documentado, no aprobación global.
- [x] Recibir corrida 17: instalación/entorno/T4 correctos; conservar errores de historial en auditoría.
- [x] Corregir clon superficial y comprobar las suites en copia limpia con historial completo.
- [x] Completar historial y preparación T4; recepción posterior con inferencia real conservada.

[Recepción de 46 revisiones y cierre explícito](evidence/domain_review46/RECEPCION.md).
El único DUDOSO se conserva en el original y se resuelve como NO en registro de
chat separado. Dominio: Sin RAG 3/22, M3 7/22, FP16 16/22, NF4 11/22 y sin
herramienta 15/22. Noventa revisiones directas y veinte equivalencias, 110 filas
resueltas sin alterar notas o gastar API. NF4 sigue rechazada. [Siguiente hito:
servicio público real](DESPLIEGUE_SIGUIENTE.md). No hace falta otra revisión de estos casos.

- [x] Recibir las 46 anotaciones humanas y preservar original y cierre de la única duda.
- [x] Recalcular los cinco perfiles con el mismo criterio y denominador 22.
- [x] Conservar tablas anteriores como historia y actualizar el reporte con tabla completa.
- [ ] Preparar, probar y publicar candidato contractual FP16 con M1, RAG/herramienta y visión.
- [ ] Verificar health/readiness, peticiones reales y W&B del servicio público.

### Candidato de despliegue 16 — preparado, ejecución real pendiente

- [x] Separar candidato de los archivos públicos de infraestructura.
- [x] Preparar empaquetado mínimo con corpus/adaptador verificados y manifiesto.
- [x] Integrar M1, QA/RAG/herramienta y visión con límites y registros sin contenido de entrada.
- [x] Probar localmente interfaz Gradio 6.32.0, errores, metadatos y verificación del ZIP con dobles de modelos.
- [x] Preparar notebook T4 sin API del juez ni cambios al Space.
- [ ] Verificar modelos reales: 16 falló en instalación; continuar con [17](DESPLIEGUE_17.md).
- [ ] Comprobar después ciclo de vida ZeroGPU, URLs y observabilidad pública real.

## Estado vigente — evaluación 14 recibida y recálculo cerrado

[Auditoría](evidence/product_14/ANALISIS.md): 110/110 notas reales, sin nuevas
consultas en este recálculo. Dominio FP16 16/22 y NF4 11/22; aceptación relativa
NF4 **rechazada** por caída 22,73 puntos, un crítico nuevo y dos regresiones, aunque
ahorra 37,60 % de memoria. Las notas no se ajustan para coincidir con humanos.
64 resultados semánticos cubiertos: 44 directos y veinte equivalencias exactas
documentadas. Quedan 46 salidas distintas pendientes de revisión de otros perfiles.
Reporte actualizado, no entrega completa. Ver [progreso vigente](PROGRESO_FINAL.md).
Los bloques cronológicos siguientes conservan estados anteriores: no son permiso
para repetir notebooks ni instrucciones vigentes de gasto. Techo actual USD 7.

- [x] Conservar y auditar ZIP/notebook 14, código, payloads, notas y presupuesto.
- [x] Recalcular dominio FP16/NF4 y controles con adjudicaciones reales.
- [x] Resolver aceptación NF4 bajo umbrales previos, sin cambiarlos.
- [x] Registrar transferencias exactas sin atribuir nuevas revisiones al usuario.
- [ ] Recibir revisión semántica de 46 salidas restantes para cerrar las tasas de otros perfiles.
- [ ] Integrar/probar servicio contractual público y observabilidad; no desplegar NF4.

## Registro cronológico de preparación y autorizaciones

Autorización vigente 19/11/2026: el usuario eleva el techo a **USD 7 TOTALES**.
[Evaluación 14 preparada](EVALUACION_14.md), sin consultas pagadas locales.
Migración con copia del registro USD 5, 57 asientos históricos intactos,
autorización registrada, 110 filas guardadas, resultados progresivos en Drive.
Conserva configuración del juez y detiene errores sin reintento de transporte.
Las referencias USD 5 anteriores quedan como historial previo, no techo vigente
de esta nueva ejecución. Pendiente ejecutar, auditar motivos y cerrar dominio.

- [x] Registrar autorización explícita de USD 7 totales, sin recarga ni liberación de reservas.
- [x] Preparar migración verificable y evaluación de los cinco perfiles completos.
- [ ] Ejecutar evaluación 14 y recibir ZIP/notebook, sin repetir corridas anteriores.

Estado vigente tras recibir archivos humanos del 19/11/2026:
[cierre humano documentado](evidence/human_closure_19/RECEPCION.md).
Juez aceptado para la tarea/configuración con límites; la aceptación condicionada
de explicación vacía se verifica en la rúbrica original sin editar la revisión.
Ocho dudas anteriores cerradas (once criterios), NF4 sigue vetado. Plan offline
de 110 payloads preparado, sin llamadas, gold ni notas inventadas. Presupuesto
USD 5 intacto: falta resolver margen antes de ejecutar evaluación del producto.

- [x] Recibir revisión humana de doce motivos y del anexo de calibración, con condiciones y límites preservados.
- [x] Cerrar únicamente once criterios DUDOSO de las ocho entradas anteriores.
- [x] Preparar los 110 registros guardados para el juez sin selección de casos ni regeneración.
- [ ] Resolver techo/conciliación de presupuesto y ejecutar evaluación completa del producto.

Última actualización 19/11/2026: [confirmación 13 recibida y auditada](evidence/confirmation_13/ANALISIS.md),
12/12 válidos dentro de rango, cero respuestas malas aprobadas. Revisión técnica
de motivos favorable; cierre humano pendiente. Acumulado USD 4,1974125
estimados/reservados. No iniciar evaluación de 110 respuestas sin resolver
presupuesto y firma humana; techo USD 5 intacto. Paquete de revisión preparado
con doce motivos nuevos y solo las ocho dudas anteriores, sin sustituir decisiones.

- [x] Conservar originales de confirmación y verificar código, notas y 57 asientos.
- [x] Recalcular confirmación con reglas previas y preparar revisión humana sin API.
- [ ] Recibir revisión humana de los doce motivos del juez.
- [ ] Recibir cierre humano del anexo de 38 motivos de calibración, sin sustituirlo por la revisión técnica de IA.
- [ ] Recibir adjudicación de las ocho dudas previas de dominio.
- [ ] Resolver presupuesto para evaluación completa sin eliminar reservas desconocidas.

Actualización vigente 19/11/2026: [Juez 12 ejecutado y auditado](evidence/paid_12/ANALISIS.md).
Calibración: 38/38 válidos, 20/20 dentro del rango, cero respuestas malas con
4–5, diferencias de longitud mitigadas 0 en seis pares. Código y notas verificadas;
USD 4,0800825 acumulados estimados/reservados, no factura. [Confirmación 13](JUEZ_13_CONFIRMACION.md)
preparada con los doce casos aprobados, sin repetir calibración ni evaluar el
producto. Pendiente ejecutarla y auditar motivos. No se declara juez validado.

- [x] Preservar ZIP y notebook ejecutado de Juez 12 y recalcular sus métricas.
- [x] Verificar notas originales, once hashes de código y conservación de presupuesto.
- [x] Preparar confirmación independiente con reglas originales y bloqueo de repetición.
- [ ] Ejecutar los doce casos, revisar motivos y conciliar presupuesto antes de evaluar el producto.

Último paso preparado: [Juez 12 en pago](JUEZ_12_PAGO.md), tras capturas de
prepago y Spend con costes demorados. No ejecutado contra Google. Conserva
ocho asientos y USD 5 totales; sin reintentos de transporte. No cambia la rúbrica,
las respuestas ni el estado de juez sin validar. No usar Juez 11 para continuar.

Actualización prioritaria 19/11/2026: [transición de facturación del juez](TRANSICION_FACTURACION.md).
Recuperación 11 ejecutada: dos 503, cero notas nuevas; ocho asientos por USD
3,6994725 estimados/reservados, no factura. Reejecución tras activar facturación
comunicada por el usuario: bloqueada antes de consultar API. No repetir Juez 11
ni borrar registros. Pendientes gasto real/estado del proyecto y continuación
versionada de pago; ejecución deshabilitada. Este estado reemplaza las cifras
de seis asientos y las referencias a facturación no activada de notas anteriores.

Plan preparado el 15/11/2026 tras leer las seis páginas de la guía `STAI_Final_Asignacion_Proyecto_integrador (1).pdf` y consultar GitHub. Estado remoto: main en `afe471739a3d9192ffb32fbb78158d473dd0d619`; M1–M3 presentes, sin carpetas M4 ni final publicadas. Esto no descarta trabajo local del equipo no compartido.

Este archivo es un plan operativo, no promesa de nota. Ya está incorporado en `final/CHECKLIST.md` en la rama `Entrega/contractrisk-final`; las fechas y responsables de ejecuciones se completarán con evidencia real. No se modifica main ni se reescriben entregas anteriores.

Actualización 18/11/2026: avance estimado **55–60 % de la entrega final**; [desglose ponderado y pendientes](PROGRESO_FINAL.md). No es nota ni conteo de casillas. Comparación 02 completa con 110 registros, antes/después NF4 y ablación reales; resultados semánticos y aceptación de eficiencia pendientes. Juez sin validar, servicio contractual público no integrado y reporte/presentación finales incompletos. El presupuesto API no cambió: USD 2,4706725 estimados/reservados, no factura, dentro del techo autorizado USD 5.

## Fechas y reglas de la guía

Último estado: [44 respuestas revisadas por el usuario](evidence/human_response_review_01/RECEPCION.md), con ocho dudas explícitas sin adjudicar. NF4 vetado para despliegue por un fallo crítico nuevo y dos regresiones de invarianza confirmadas; FP16 no se declara aprobado. [Juez 11](JUEZ_11_RECUPERACION.md) preparado con diagnóstico de transporte y presupuesto acumulado dentro de USD 5, sin facturación habilitada ni nuevas llamadas locales. Verificación actual: **226 pruebas final + 128 M3 = 354 aprobadas**; no prueban disponibilidad ni calidad del servicio de API.

- [x] Recibir/preservar revisión humana de 44 salidas, transcribir criterios y conservar dudas; no sustituir el dictamen por notas LLM.
- [x] Registrar veto de selección NF4 bajo reglas previas, separado del `not_evaluable` de la evaluación numérica completa.
- [ ] Adjudicar ocho dudas y conciliar pertinencia de citas frente al respaldo de afirmaciones; no cambiar referencias para aprobar resultados.
- [x] Preparar recuperación 11: nota válida intacta, ledger con seis asientos anteriores, marcador exclusivo, timeout/red/JSON/HTTP diferenciados y un reintento 503 global.
- [ ] Ejecutar recuperación 11 en CPU, conservar resultados y auditar notas; solo tras aprobar regresión y razones continuar con confirmación independiente.

Actualización vigente: avance estimado **55–60 %**, según [desglose](PROGRESO_FINAL.md). [Comparación 02 completa y auditada](evidence/comparison_02/ANALISIS.md): 110 registros, memoria/latencia y ablación reales; diagnóstico recalculado, no scorecard semántico final. NF4 no aceptado para despliegue. Revisión humana de 44 respuestas y juez/dominio pendientes. [Reporte integrador](reporte.md) en borrador. Verificación actual: 214 pruebas final + 128 M3 = 342 aprobadas.

- [x] Conservar ZIP/notebook de Comparación 02, verificar 88 hashes, manifiestos y recalcular tablas por caso sin inferencia.
- [x] Documentar ahorro 37,6 % de memoria y aumento 42,7 % de mediana NF4, sin convertirlos en aprobación global.
- [x] Auditar ablación: dos cálculos correctos también sin herramienta; no atribuir mejora de exactitud no demostrada.
- [x] Corregir métricas de router/resultado/éxito para futuras ejecuciones y derivar cifras históricas sin reescribir W&B ni respuestas.
- [x] Preparar borrador de reporte y revisión humana de 44 respuestas reales, sin inventar revisiones ni notas LLM.
- [ ] Recibir revisión de respuestas, completar juez validado/dominio y decidir versión final; no aceptar cuantización solo por ahorrar memoria.

Actualización: [Comparación 01 auditada](evidence/comparison_01/ANALISIS.md), error del adaptador durante calentamiento; cero filas evaluadas. [Comparación 02](COMPARACION_02.md) corrige la interfaz de funciones M3 sin cambiar modelos/datos/reglas. Preparada, todavía sin inferencia real. Verificación actual: 210 pruebas final + 128 M3 = 338 aprobadas, incluyendo fábrica y wrappers reales con modelos simulados. No hay eficiencia aceptada ni juez validado. Revisión humana de doce ejemplos cerrada, sin inferencia de confirmación.

- [x] Recibir revisión de doce ejemplos: once aprobados en archivo y cierre posterior explícito del caso de explicación ausente; conservar ambos registros.
- [x] Preparar ejecutor sin API para 22 casos por perfil, campos de memoria/latencia, errores retenidos y resultados separados por modalidad.
- [x] Predeclarar reglas de dominio y daño antes de la comparación; ejecución semántica y enlace de juez siguen pendientes.
- [x] Ejecutar y auditar Comparación 01: carga y prueba pequeña NF4 reales; fallo de interfaz en calentamiento, sin evaluar casos. No equivale a comparación completada.
- [x] Reproducir/corregir fallo de funciones M3 y reemplazar el doble de prueba incorrecto; conservar originales y verificar configuración sin cambios semánticos.
- [x] Ejecutar y auditar Comparación 02 en T4: cinco perfiles, 110 registros. Tablas técnicas completas; calidad semántica y aceptación de eficiencia siguen pendientes.

Verificación registrada en Hydrogen 10: **193 pruebas final + 128 M3 = 321 aprobadas**. [Corrida auditada](evidence/hydrogen_10/ANALISIS.md): nota 2 reutilizada, 503 y reintento con fallo de transporte/JSON, cero notas nuevas. USD 2,4706725 estimados/reservados, no cargos confirmados; techo USD 5 intacto. No repetir 07–10 ni borrar registros Drive. La revisión humana separada se cerró después; no se ha ejecutado la confirmación.

- [x] Conservar ZIP/notebook originales de Hydrogen 09 y auditar la nota válida y el 503.
- [x] Preparar continuación sin regenerar notas válidas, con reintentos acotados, reservas acumuladas y pruebas de regresión técnicas.
- [x] Ejecutar y auditar continuación 10; conservar nota previa y fallos técnicos sin inventar resultados.
- [ ] Resolver disponibilidad con diagnóstico controlado; completar calibración, auditar razones y confirmar 12 casos revisados antes de validar el juez. La corrida 10 no superó el piloto porque quedó incompleta, no por una nota incorrecta.
- [ ] Congelar/ejecutar comparación común, ablación y eficiencia; integrar despliegue contractual real y cerrar reporte/presentación/reproducción/entrega. El detalle de cada fase se conserva abajo.

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
- [x] Confirmar trabajo M4/M5 externo: el usuario indica que no hay desarrollo fuera de GitHub. No equivale a módulos M4/M5 completados.
- [ ] Recibir los materiales/labs de sesiones 13 y 15 y, si existen, los de visión e invarianza de M4.
- [x] Confirmar disponibilidad de Colab GPU para comparar antes/después: usuario confirma T4 el 16/11; acceso efectivo se registrará al ejecutar.
- [x] Confirmar cuentas y acceso inicial: Space `Juanoff/contractrisk-colombia` ejecuta prueba real ZeroGPU; W&B `jcramonp-eanit/contractrisk-final` muestra una run. [Evidencia y límites](evidence/SPACE_SMOKE_CONFIRMADO.md). Acceso externo W&B y series de métricas pendientes; no se autorizaron pagos.
- [ ] Acordar responsabilidades humanas y disponibilidad de ambos integrantes.
- [x] Crear rama `Entrega/contractrisk-final` desde main remoto `afe4717`; entregas anteriores preservadas.
- [ ] Inventariar modelos/adaptador, licencias, paquetes, corpus y evidencias existentes.
- [x] Ejecutar pruebas heredadas: 128 pruebas M3 aprobadas el 16/11; snapshots M1–M3 preservados. No es nueva evaluación de modelos.
- [x] Abrir checklist operativo en `final/` con evidencias por casilla.

Aceptación: base identificada, sin cambios ajenos perdidos, inventario y responsables reales. No publicar claves ni materiales privados del curso.

## Fase 1 — definir el producto y desplegar un esqueleto temprano

- [x] Usuario objetivo documentado en README raíz: analista/auditor que consulta fichas y prioriza revisión humana, sin decisión automática de fraude. No supone validación externa con usuarios.
- [ ] Definir una decisión y una métrica de éxito de usuario: proporción de consultas con respuesta respaldada y sin afirmaciones indebidas; alertas omitidas y abstención reportadas aparte. Congelar definición operativa.
- [x] Interfaz de desarrollo común `IntegratedSystem.predict(question, image, mode, description)` con resultado estructurado y regresiones CPU; ejecución de texto/visión T4 conservada. Publicación del mismo punto de entrada pendiente.
- [x] Modos definidos/implementados: QA, comparación numérica por herramienta, suficiencia M1 y QA con imagen; no todos están expuestos aún en Space.
- [x] Formatos de citas, errores, incertidumbre y abstención implementados/validados por esquema; detectar soporte semántico de todas las citas continúa pendiente.
- [x] Crear Space mínimo y comprobar arranque de interfaz y operación GPU según capturas del usuario. [Prueba inicial](evidence/SPACE_SMOKE_CONFIRMADO.md). Todavía no ejecuta el pipeline contractual.
- [ ] Probar instalación y carga en el hardware elegido; medir memoria y arranque.
- [ ] Registrar la decisión si se requiere una versión reducida, con exclusiones exactas; no presentarla como idéntica al sistema completo.

Aceptación: URL accesible y flujo mínimo real. Un mock, un notebook enlazado o respuestas guardadas no sustituyen la demo de inferencia.

## Fase 2 — integrar y corregir comportamiento sin alterar evidencia histórica

Avance de preparación: se añadieron `integration.py`, `adapters.py`, `run_integration.py`, configuración con revisiones fijas y [notebook de integración 01](ContractRisk_Final_Integracion_01_Colab.ipynb). 18 pruebas final CPU y 128 heredadas aprobadas; sintaxis y generación de fixtures comprobadas. Los modelos reales no se han ejecutado en esta nueva integración. No marcar las casillas siguientes como verificadas hasta revisar el ZIP de T4. La orquestación visual de este ensayo reutiliza extracciones guardadas, no mide latencia multimodal fresca.

Actualización: integración 01 ejecutada en T4 con código `753e05e`, 14 filas y cero excepciones de caso. [Auditoría y hallazgos](evidence/integration_01/ANALISIS.md). Texto, cálculo y carga M1 comprobados en desarrollo; extracción visual válida 0/4 y preguntas visuales abstienen por formato. Calidad visual no aprobada, no sustituir Space ni marcar integración completa. La corrección de fuentes se ejecutó; siguen pendientes separación OCR/campos y restricción del router.

Corrección 02 ejecutada y auditada: [evidencia original](evidence/correction_02/ANALISIS.md), [protocolo y límites](CORRECCION_02.md). Once registros, sin excepciones, tres lecturas nuevas válidas y una imagen uniforme bloqueada sin VLM; tres respuestas visuales correctas en esta muestra y una abstención. Cálculo correcto con una herramienta; consulta simple sin router. W&B desactivado por secreto inaccesible. Las respuestas visuales reutilizan lecturas; no es medición fresca de extremo a extremo ni aprobación final. 34 pruebas CPU final y 128 M3 pasan tras preparar candidatos; los logs de T4 contienen las 32 final y 128 M3 vigentes en aquella corrida.

- [x] Conservar sin editar ZIP y notebook ejecutado de corrección 02; verificar hashes y fuentes.
- [x] Preparar diez candidatos visuales con cinco fichas diferentes, dos variantes invariantes y casos ausente/vacío/adversarial, sin nueva inferencia. [Revisión humana pendiente](eval/visual_candidates_v1/REVISION_HUMANA.md).
- [x] Recibir revisión humana de cada candidato: Juan Camilo Ramon Perez, 16/11/2026; diez aprobados. [Original y dictamen](VISUAL_03.md). Se congelaron hashes de las entradas y referencias de este subconjunto, no el protocolo final completo.
- [x] Preparar [prueba visual 03](ContractRisk_Final_Visual_03_Colab.ipynb): lecturas nuevas, carga conjunta por comprobar, memoria/latencia sincronizadas, evaluación separada de inferencia. 42 pruebas final CPU + 128 M3 pasan; incluye comprobación de fallo temprano sin secreto. [Protocolo y límites](VISUAL_03.md).
- [x] Ejecutar visual 03 en T4 y auditar resultados: diez casos, carga conjunta sin OOM, memoria y tiempos registrados; W&B sincronizado según logs. [Evidencia](evidence/visual_03/ANALISIS.md). Acceso externo/dashboard pendiente. Un error monetario crítico se conserva; no se modificó Space.
- [x] Añadir [control de contradicciones 0.3](CONTROL_CONSISTENCIA.md), posterior a inspección del fallo, y reproducir diez lecturas guardadas en CPU: vis_04 se bloquea, las otras nueve salidas se conservan. 53 pruebas final + 128 M3 pasan. No es nueva inferencia ni reparación del OCR.
- [x] Umbrales aprobados por el usuario antes de comparar: pérdida máxima 5 puntos porcentuales de cumplimiento, cero fallos críticos nuevos ni regresiones en controles, ahorro mínimo 20 % de memoria pico CUDA asignada. [Política y condiciones](EFICIENCIA.md). Medición pendiente; no son exigencias numéricas de la guía.
- [x] Preparar decisión de aceptación que rechaza datos incompletos/no comparables y juez sin calibración. Pruebas sintéticas de límites y regresiones: total 66 final CPU + 128 M3 aprobadas; no son resultados de modelos cuantizados.

- [ ] Conectar el clasificador RoBERTalex+LoRA de M1 con un caso de uso real y visible; mantener sus etiquetas y límites.
- [ ] Conectar corpus/indexación, recuperación híbrida, reranking y herramienta M3 en el mismo servicio.
- [x] Revisar campos completos en desarrollo: cálculo de corrección 02 cita ambos operandos; en vis_04 el monto correcto sí llegó y la causa fue lectura/propagación, no recuperación. Evaluación general común todavía pendiente.
- [ ] Implementar controles de respuesta sustentada: comprobar disponibilidad del dato, citas y ausencia de afirmaciones fuera del corpus.
- [ ] Tratar preguntas de cláusulas o auditorías ausentes y entradas fuera de alcance; corregir o reportar el fallo de abstención con pruebas reales.
- [ ] Incorporar extracción desde imágenes con validación de ID, montos y legibilidad.
- [ ] Evitar que instrucciones maliciosas en preguntas o imágenes se ejecuten como instrucciones de sistema.
- [ ] Mantener esquema de herramienta, tolerancia de JSON y límites de pasos, tiempo e intentos.
- [ ] Pruebas de regresión para falsos positivos de números, negaciones y acusaciones.
- [x] Conservar resultados M3 originales y corridas finales de desarrollo sin editar; cambios en `final/` con versiones/metadata y auditorías separadas.

Aceptación: texto e imagen se procesan de punta a punta; el usuario puede ver qué dato provino de qué fuente. Una advertencia no equivale a solucionar una alucinación.

## Fase 3 — evaluación común y criterios antes de optimizar

Preparación posterior a visual 03: [protocolo de juez y conjunto común](JUEZ_Y_EVALUACION_FINAL.md). 22 entradas ensambladas (12 QA + 10 visuales) con referencias separadas; no se cambiaron vis_04 ni notas previas para favorecer el control. Veinte anclas aprobadas: 19 por archivo con fecha declarada 16/11 y una por confirmación posterior del 17/11. Se explicitó la regla de explicación vacía máxima 2 en rúbrica 1.1, sin clamp de notas, y la cita por chunk_id. [Notebook de calibración preparado](ContractRisk_Final_Calibracion_Juez_Colab.ipynb): 38 juicios previstos, carga/kernel NF4 reales y calibración T4 no ejecutados aún. 85 pruebas final CPU + 128 M3 aprobadas; no son resultados del modelo nuevo.

- [x] Ensamblar candidato común con procedencia/hashes y sin respuestas esperadas en entradas del sistema. No está congelado aún el protocolo/harness completo.
- [x] Preparar rúbrica nueva y calibración sintética separada, sin indicadores de acierto enviados al juez y sin sustituir notas.
- [x] Recibir [revisión humana de veinte anclas](eval/calibration_review_v1/REVISION_CALIBRACION.md); conservar original y [confirmación posterior de empty_explanation_bad](evidence/calibration_review_01/CIERRE.md), sin simular veinte aprobaciones en el archivo recibido.
- [x] Ejecutar primer filtro T4 y auditar razones: [Qwen 7B rechazado](evidence/judge_calibration_01/ANALISIS.md), 38/38 válidos, 15/20 en rango, cinco respuestas malas con 4–5 y dos pares fuera de límite. Notas intactas; no se aprueba calidad/eficiencia.
- [x] Preparar [regresión Mistral](JUEZ_02.md), modelo de otra familia, sin cambiar rúbrica/anclas/umbrales; fijar doce ejemplos nuevos de confirmación antes de observar Mistral. 93 pruebas final CPU + 128 M3 aprobadas; no inferencia nueva.
- [x] Ejecutar Mistral y auditar resultados: [corrida conservada](evidence/judge02_legacy/ANALISIS.md), 11/20 en rango, ocho respuestas malas con notas altas y máximo 3 de diferencia. No valida al juez.
- [x] Diagnosticar entrada con tokenizers reales sin GPU: Mistral 38/38 mensajes con BOS extra y Qwen 0/38; corregidos 38/38 nativos en ambos. Conteos antiguos Mistral reconstruidos coinciden con registros originales. No demuestra cuánto explica las notas.
- [x] Preparar [comparación controlada Mistral corregida](MISTRAL_TOKENFIX.md): mismo modelo/rúbrica/anclas/umbrales, preflight real obligatorio antes de pesos y equivalencia nativa en cada llamada. Cargador y M3 históricos preservados. 100 pruebas final CPU + 128 M3 aprobadas; ninguna nueva inferencia.
- [x] Ejecutar notebook corregido una vez y auditar razones, tokens y comparabilidad del entorno: [original y auditoría](evidence/mistral_tokenfix/ANALISIS.md), 38 entradas nativas pero calibración rechazada. No aceptar juicio por equivalencia de tokens solamente.
- [x] Preparar [juez por criterios y razonamiento](JUEZ_RAZONAMIENTO.md), piloto de siete con parada al primer fallo, conservación de notas y regresión completa condicionada; tokenizer real comprobado en CPU, sin pesos.
- [x] Ejecutar piloto Qwen3-8B y 38 juicios en T4: [corrida 04 auditada](evidence/reasoning_04/ANALISIS.md), piloto aprobado, regresión rechazada; 19/20 no basta por falsa atribución aprobada, verbosidad y defectos de razones.
- [x] Preparar [versión 05 con respaldo literal](JUEZ_RESPALDO_LITERAL.md), sin cambiar notas ni umbrales. Normalización solo de bloques enteros idénticos; 38 entradas nativas y seis pares normalizados idénticos comprobados sin pesos.
- [x] Auditar ejecución 05: siete anclas ejecutadas en rango; detención por fuente diagnóstica disponible no citada por la respuesta. [Original y diagnóstico](evidence/literal_05/ANALISIS.md); no se ejecutaron las otras dos ni la regresión.
- [x] Versionar evaluador 1.1 y recalcular las siete salidas en CPU sin generar ni cambiar notas. No confundir fragmento diagnóstico con cita de la respuesta; seguir rechazando fuentes desconocidas y citas inventadas. [Recálculo](evidence/literal_05/replay_1_1.json).
- [x] Preparar [continuación 06](JUEZ_CONTINUACION_06.md), mismo modelo/prompt/decodificación y entorno comprobado, siete salidas reutilizadas sin selección.
- [x] Auditar continuación 06: un juicio nuevo, attribution_bad=4 pese a explicación falsa reconocida; detención correcta. El último piloto y los 29 juicios no se ejecutaron; no se acepta el juez ni se repite buscando mejores notas.
- [x] Registrar autorización de API hasta USD 5 totales, sin recargas; preparar registro local persistente de reservas y pruebas. No hay cliente de pago conectado ni llamadas realizadas.
- [x] Preparar cliente REST y [notebook API 07](ContractRisk_Final_Juez_07_API_Colab.ipynb), candidato fijo, sin pago habilitado, sin retries de red ni fallback, confirmación explícita de proyecto gratuito y registro/marca persistentes en Drive. Clave confirmada por usuario como guardada en Colab, valor no conocido.
- [x] Auditar intento API 07: primera generación HTTP 503, cero notas y reserva USD 0,3072 conservada. No permite concluir calidad ni demostrar cargo. [Original y auditoría](evidence/api_07/ANALISIS.md).
- [x] Preparar [reintento único API 08](JUEZ_API_08_REINTENTO.md) tras autorización de continuación: mismo cuerpo/modelo/prompt/umbrales, marcas antiguas intactas y presupuesto de calibración acumulado, sin modo pagado.
- [x] Auditar recuperación 08: un segundo 503, cero notas, reserva acumulada USD 0,6144 preservada; no se repite. [Evidencia](evidence/api_08/ANALISIS.md).
- [x] Leer catálogo aportado por usuario y documentación oficial; fijar Hydrogen como candidato NUEVO tras dos errores de disponibilidad, sin seleccionar entre notas. Preparar [notebook 09](ContractRisk_Final_Juez_09_Hydrogen_Colab.ipynb), mismo gold sintético/rúbrica/umbrales, historia y Drive verificados.
- [ ] Ejecutar calibración Hydrogen 09, auditar notas/razones/verbosidad y consumo; solo si supera regresión revisar/ejecutar confirmación nueva. No se ha probado inferencia de Hydrogen todavía.
- [ ] Configurar acceso a candidato de API, probar primero nivel gratuito con anclas sintéticas y auditar calibración. No activar facturación sin verificar controles y techo total.
- [x] Recibir y cerrar revisión humana de doce ejemplos separados; [original y cierre](evidence/confirmation_review_01/CIERRE.md), hashes en el paquete de confirmación.
- [ ] Si supera regresión: ejecutar confirmación y auditar razones antes de aceptar juez final. Los doce ejemplos están aprobados, pero no ejecutados.

- [x] Diseñar veinte anclas sintéticas separadas de los 22 casos comunes; revisión humana recibida y conocimiento previo del gold M3/visual declarado. Inferencia y auditoría del juez pendientes.
- [x] Ensamblar ampliación candidata de 22 entradas con casos textuales/visuales, adversariales, ausentes y pares; selección visual documentada antes de inferir, referencias conservadas incluso ante vis_04. Protocolo/harness completos por congelar.
- [x] Implementar base candidata de harness común: hashes de imágenes/paquete, frontera sin gold, errores en denominador, cobertura literal conservadora, notas brutas y dominio desconocido sin validación. Pruebas CPU no son corrida de modelos ni scorecard final.
- [x] Ejecutar 22 casos por perfil y conservar protocolos/hashes de colección y evaluación por separado. El cruce semántico se implementa después; no afirmar una congelación ciega completa previa a la colección.
- [x] Revisión humana de imágenes, respuestas esperadas/criterios, procedencia y privacidad del subconjunto visual v1: diez casos aprobados por el usuario el 16/11. Representaciones sintéticas marcadas; no incluye aprobación de respuestas del modelo ni del conjunto final completo.
- [x] Definir/ejecutar invarianza visual v1: contraste 0.85 y rotación de 1 grado, dos pares revisados por usuario y medidos en visual 03. Ambos conservan campos/respuestas, incluso las tildes añadidas erróneamente en uno; invarianza no equivale a corrección. Repetición en versión eficiente pendiente.
- [x] Documentar abstención explícita de líneas base sin visión, sin transcripción gold ni cambios de denominador.
- [x] Registrar 22 casos, una pasada ordenada, warm-up, parámetros/caché y limitación de p95; no garantizar estabilidad de latencia.
- [ ] Congelar gold, harness, prompts de evaluación, métricas y hashes antes de ejecutar la comparación final.
- [x] Mantener cobertura literal, nota cruda LLM y dominio como dimensiones distintas. Dominio aún pendiente para perfiles sin revisión completa.
- [x] Validar el juez con calibración/confirmación separadas y cierre humano con límites documentados.
- [x] Aplicar la misma versión de juez a las 110 salidas guardadas sin renombrar notas históricas ni regenerar sistemas.
- [ ] Registrar calidad automática, calidad sustentada según juez, dominio, abstención, adversariales, invarianza y casos con imagen.
- [x] Fijar pérdida máxima y ganancia mínima antes de medir: aprobación explícita del usuario, registrada en `efficiency_policy.json`. El gold/harness comunes y la calibración aún no están cerrados; la política no puede aplicarse al proxy literal de visual 03.

Aceptación: protocolo versionado, sin sustitución de notas ni mezclas de métricas/hardware. Si el juez falla calibración, no usarlo como evidencia de calidad validada.

## Fase 4 — perfilado, técnica de eficiencia y medición

- [ ] Perfilar latencia y memoria por componente sobre el sistema integrado previo a optimizar; si no existe M4 anterior, declarar esta nueva base visual.
- [x] Elegir NF4 a 4 bits como técnica candidata sobre el mismo generador, cómputo FP16; loader preparado con verificación de capas y sin fallback. No se ha medido/aceptado ni desplegado. LoRA histórico M1 no se usa como evidencia de mejora nueva.
- [x] Conservar antes FP16 y después NF4 de Comparación 02: mismos casos/modelos/recuperación/prompt y VLM, salvo precisión del generador; respuestas sin editar.
- [ ] Validar compatibilidad real de la técnica con el hardware y licencias de distribución.
- [x] Ejecutar FP16/NF4 en la misma T4 y conjunto, con memoria, tiempos, condiciones y calentamientos registrados. Esto no cierra la evaluación semántica.
- [x] Guardar por petición notas, latencia/memoria y componentes; p50/p95 y pico CUDA con unidades y origen de hardware claros.
- [x] Evaluar abstención, resistencia a inyección e invarianza en NF4 y FP16. No confundir falta de completitud con obedecer una inyección.
- [x] Aplicar los umbrales previos: NF4 rechazada por dominio, crítico nuevo e invarianza.
- [x] Conservar resultado negativo y excluir NF4 del despliegue. FP16 sigue como candidato, no aprobación global ni servicio ya publicado.

Aceptación: tabla antes/después calculada desde registros, umbral previo trazable y decisión basada en evidencia. No prometer mejora antes de medir.

## Fase 5 — tabla evolutiva, ablación y análisis

- [x] Ejecutar cinco perfiles sobre las mismas 22 entradas; 110 notas de juez. Mantener pendientes las tasas de dominio aún sin revisión completa.
- [x] Mantener métricas M1/M2 de clasificación separadas de QA, sin mezclar Macro F1 y cobertura de hechos.
- [x] Registrar medianas y subconjuntos texto/imagen con denominadores; explicar notas altas por abstención de modelos sin visión.
- [x] Ablación de herramienta medida en Comparación 02: 20 salidas idénticas y dos cálculos correctos también sin herramienta; aporta traza explícita, no mejora de exactitud demostrada en estos dos casos.
- [ ] Analizar al menos cinco fallos reales agrupados por extracción visual, recuperación, generación, herramienta o evaluación; indicar componente y reparación propuesta.
- [ ] Reevaluar RAGAS si se comparan respuestas nuevas y se reporta su delta; no atribuir métricas M3 a la versión final.
- [x] Conservar respuestas, contextos, imágenes/referencias permitidas, trazas, versiones y resultados reales por caso, con recálculo sin inferencia.

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
