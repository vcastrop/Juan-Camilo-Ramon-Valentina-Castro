# Auditoría de integración v5 y calibración

Fecha: 29/10/2026. Revisión técnica asistida por Codex; no sustituye revisión humana del equipo. ZIP y notebook originales conservados junto a este archivo. No es evaluación del gold final ni scorecard de entrega.

## Integridad y ejecución

- Corrida T4, 07:05:49–07:14:49 UTC; semilla 42, Qwen2.5-3B-Instruct en las cuatro variantes y como juez en llamadas separadas.
- Los 23 hashes de fuentes declarados coinciden con el paquete de código v5 entregado (commit f62e969).
- Notebook sin salidas de error; log con 62 pruebas aprobadas. 133 chunks; corpus con hash 7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505.
- 32 predicciones: cuatro variantes por ocho preguntas de desarrollo. 48 juicios: 12 pares breve/repetido, antes y después del control de verbosidad. Resumen de calibración recalculado desde detalle: coincide exactamente.

## Generación y agente

| Variante | Formato inicial | Formato final | Mediana por consulta (s) |
|---|---:|---:|---:|
| Sin RAG | 7/8 | 8/8 | 3,956 |
| Denso | 8/8 | 8/8 | 6,298 |
| Avanzado | 8/8 | 8/8 | 7,574 |
| Agente | 8/8 | 8/8 | 9,891 |

Medianas sobre todos los casos, incluido error semántico; excluyen carga y juez. No son tiempos del gold ni una comparación de eficacia global.

Avanzado y agente responden correctamente las cuatro modalidades; el denso no responde correctamente ninguna. El agente llama a la herramienta en ambos cálculos y reproduce 75.233.920 COP y 226.596.000 COP correctamente. Hay una consulta ordinaria de modalidad (índice 2) resuelta con decisión `answer` inicial y sin herramienta: queda demostrada la ruta de dos consultas con herramienta y una sin ella. La segunda respuesta de cálculo no cita ambos fragmentos `tool_value`: la evidencia de ambos operandos está disponible en la traza, pero la selección de citas necesita evaluación de sustento, no solo validación de IDs.

Persisten tres llamadas innecesarias rechazadas por ID vacío (índices 0, 1 y 3); el controlador se recupera en el paso 3. Son 3/6 consultas sin necesidad de cálculo; las otras tres deciden `answer` inicialmente. No hubo omisión de las dos llamadas necesarias. El formato válido no demuestra pertinencia ni veracidad.

Fallos críticos: avanzado/agente no se abstienen ante clausulado ausente (índice 6), aunque la explicación reconoce la ausencia; inventan una conclusión de auditoría (índice 7) a partir del estado de la ficha. Sin RAG produce cifras incluso con `abstencion=true`; denso atribuye datos de otros contratos. No declarar abstención validada ni preparación para uso operativo.

## Juez: salida real, sin corrección de notas

| Control | Antes | Después |
|---|---:|---:|
| Juicios válidos al primer intento | 24/24 | 24/24 |
| Diferencia absoluta media breve/repetido | 0,583 | 0,833 |
| Diferencia firmada media (repetido menos breve) | -0,417 | -0,667 |
| Diferencia absoluta máxima | 1 | 1 |
| Respuestas breves dentro del rango diagnóstico | 11/12 | 10/12 |

La mitigación probada NO redujo el efecto de longitud. Que ninguna diferencia supere un punto no prueba ausencia de sesgo. Son pares sintéticos de repetición literal, no todas las formas de verbosidad; los rangos son expectativas diagnósticas propuestas, no calificaciones humanas gold.

Revisión de las 48 razones: `wrong_2` repetido recibe 4 antes y después pese a afirmar 120000 frente a 12000 de la fuente. Su versión breve recibe 3 y reconoce la discrepancia. `wrong_0` propone Compraventa y no explica; el juez llega a llamarla correcta y, después del control, le atribuye Selección abreviada, confundiendo la evidencia con la respuesta evaluada. Las ocho variantes breves de abstención reciben 5; algunas razones de sus versiones repetidas objetan abstenerse o piden extensión innecesaria. Se registran estas contradicciones, no se ajustan puntuaciones automáticamente.

El juez ya no recibe un indicador de acierto ni reemplaza su nota por accuracy, pero su calidad semántica no queda aprobada. Comparte modelo con el generador: llamadas separadas no garantizan independencia de errores ni eliminan autopreferencia.

## Continuación

1. Preservar esta corrida como diagnóstico y añadir casos de regresión para abstención, cifras y confusión entre respuesta/evidencia del juez.
2. Ajustar de forma acotada instrucciones/validación, probar sobre desarrollo y calibración, no sobre gold; no perseguir notas altas ni transformar notas del juez.
3. Implementar y congelar métricas automática y de dominio, harness común y las cuatro métricas RAGAS con denominadores y N/A definidos.
4. Ejecutar comparación final sobre las mismas 12 preguntas gold; conservar todos los fallos, tiempos y justificaciones.
5. Completar documentación, declaración de IA, reproducción y revisión del PR. Main no se modifica en esta auditoría.
