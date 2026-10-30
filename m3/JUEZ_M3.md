# Juez QA independiente — candidato m3-judge-1.0

Implementación: `judge.py`. Estado: probado con generadores simulados, NO calibrado ni ejecutado con un LLM real todavía. Esta dimensión no produce actualmente un scorecard final.

## Qué evalúa

Evalúa si la respuesta propuesta y su explicación son pertinentes y están respaldadas por las fuentes que recibió el sistema. No califica cuán detallada es una ficha por sí sola. Recibe pregunta, respuesta, explicación, citas, abstención, fragmentos y operaciones de herramientas. No recibe la etiqueta esperada, el resultado del verificador automático, confianza del clasificador, notas anteriores ni un indicador de coincidencia con el gold. La construcción del mensaje usa una lista explícita de campos permitidos.

| Nota | Ancla |
|---|---|
| 1 | Respuesta esencialmente incorrecta, inventada, explicación ausente o contradictoria; acusación no sustentada. |
| 2 | Contenido parcialmente pertinente, pero error importante o explicación/citas sin sustento del hecho central. |
| 3 | Respuesta útil pero incompleta o con sustento insuficiente de una parte relevante. |
| 4 | Respuesta y explicación pertinentes y sustentadas, con citas verificables o abstención justificada; solo omisiones menores. |
| 5 | Respuesta precisa y completa respecto a lo preguntado y a la evidencia, explicación verificable, citas pertinentes y límites apropiados. Una abstención justificada también puede merecer 5. |

Formato solicitado: `{"puntaje": 1, "razon": "Explicación específica del veredicto"}`. El lector también admite dos líneas inequívocas PUNTAJE= y RAZON=, acento en RAZÓN y coma final tras la nota. Rechaza múltiples objetos, claves duplicadas, notas booleanas/decimales/fuera de rango, razón vacía y puntajes repetidos ambiguos.

## Corrección de M2

La nota no se cambia por acertar o fallar. Solo hay un reintento por formato inválido, nunca por una nota baja. Se preservan ambas salidas. Si ambos intentos fallan, score y reason son null; no se rellenan con 0, 3, 4 ni 1. El resumen informa promedio entre notas válidas junto con cobertura, ausentes, tasa del primer intento y tasa final, siempre sobre todos los casos. Un promedio con fallos no equivale al promedio de todo el conjunto.

Las instrucciones incluyen un control explícito contra premiar longitud, repetición y tono seguro. Se puede desactivar ese control para una comparación pareada antes/después. Su eficacia está pendiente de una prueba multicaso con contenido equivalente y notas brutas; no se da por demostrada por estar escrita en el prompt.

## Límites y calibración pendiente

La independencia aquí es del veredicto respecto al indicador de acierto automático, NO prueba independencia estadística ni uso de otra familia de modelo. Debe registrarse el modelo y revisión reales cuando se ejecute. Usar la misma familia que el generador conserva riesgo de preferencias compartidas.

Una abstención puede ser apropiada respecto a un contexto insuficiente aunque exista la respuesta en el corpus completo: este juez observa el paquete entregado, no busca en todo el corpus. La métrica de cobertura/corrección y el análisis de recuperación deben detectar ese fallo; no se debe alterar la nota del juez para ocultarlo ni presentarla como calidad integral.

Pendiente: ejemplos de calibración separados del gold, revisión humana de orientación de notas y razones, prueba de verbosidad en varios pares, versión definitiva congelada e integración en el harness de las cuatro variantes. La sintaxis válida no garantiza un juicio semánticamente correcto.
