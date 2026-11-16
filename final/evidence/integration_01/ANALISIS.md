# Integración 01: ejecutada, calidad visual no aprobada

Corrida: 16/11/2026 18:14:58–18:21:05 UTC, Tesla T4, Python 3.13.16, torch 2.14.1+cu130. Código `753e05e`. [Archivo original](original_results.zip), [auditoría](audit.json). W&B: https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/nt77qjbf

Se verificaron integridad ZIP, 14 filas únicas, hashes de cinco fuentes Python frente al commit, cuatro imágenes frente al manifiesto, corpus y adaptador frente a archivos locales. No se editaron respuestas ni notas. El escaneo acotado de patrones de credenciales en texto del ZIP no encontró coincidencias; no es certificación absoluta de privacidad.

## Qué funcionó

- El fallo de fuente quedó superado: cuatro imágenes generadas y leídas por el VLM real.
- M1 cargó el adaptador real y produjo dos señales plausibles en ejemplos sintéticos: REQUIERE_REVISION y SUFICIENTE. No hay evaluación estadística ni calibración de confianza en estos dos casos.
- Consulta de modalidad: Mínima cuantía, con cita a la ficha completa. Latencia de etapa 13,43 s.
- Herramienta: `abs(77000000 - 1766080) = 75233920 COP`, respuesta y explicación concordantes y dos citas de campos fuente. Latencia 10,12 s.
- Las consultas por auditoría ausente y contrato desconocido se bloquearon mediante controles deterministas, no por comprensión demostrada del generador.
- W&B registra finish y sincronización en el log. Su estado de dashboard no fue inspeccionado por el agente. Las métricas de éxito técnico no equivalen a calidad de respuesta.

## Fallos concretos

1. Las tres imágenes legibles produjeron legible/texto_visible, pero omitieron id_contrato, objeto, modalidad y valor_cop. El JSON podía interpretarse, pero no cumplía el esquema requerido: 0/4 extracciones válidas contando la imagen vacía.
2. La imagen vacía llevó al VLM a inventar transcripción, identificador, modalidad y valor. El validador rechazó el ID inválido y no dejó pasar la extracción a generación. Esto es protección del sistema, no abstención correcta del VLM.
3. Las cuatro orquestaciones visuales terminaron en abstención por formato. En las tres fichas legibles es un fallo funcional: todavía no podemos afirmar que responde consultas visuales.
4. La pregunta de modalidad provocó una decisión de router malformada y una llamada innecesaria a la herramienta con segundo ID vacío; fue rechazada y luego respondió correctamente. `components.tool=true` significa que hubo un intento, no una herramienta útil.
5. Las fases visuales reutilizan lecturas guardadas y se abstuvieron sin generador. Sus ~0,01 s no son rapidez de inferencia multimodal. No compararlas con latencias de M3 ni de eficiencia.

## Lectura del estado

`failures=[]` significa que ningún caso lanzó excepción capturada. No cuenta errores de esquema ni equivocaciones semánticas. `quality_approved=false` se mantiene. La integración recorrió las etapas, pero no está lista para sustituir el Space inicial ni pasar al scorecard final.

Advertencias no fatales: telemetría interna Chroma/PostHog incompatible, aviso de dtype y conflicto de bigframes con python-dateutil. No causaron un traceback en esta corrida, pero deben corregirse/aislarse para el entorno final, no confundirse con éxito de las respuestas.

## Ruta siguiente

Conservar esta corrida y crear versión nueva. Separar la transcripción visual de la extracción de campos, validar campos contra el texto observado sin rellenar desde gold/corpus, rechazar imágenes vacías antes de inferencia y conservar el juicio del VLM cuando se ejecute. Restringir el uso de herramienta a la operación que admite. Registrar aparte excepción, formato válido, abstención justificada y calidad. Probar primero las respuestas reales guardadas en CPU como regresiones y después repetir solo las etapas necesarias en T4 con trazabilidad nueva.
