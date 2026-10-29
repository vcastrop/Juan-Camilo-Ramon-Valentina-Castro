# RAGAS didáctico: adaptación explícita de S10

Estado: código candidato `ragas_course.py`, probado con dobles sintéticos, pendiente integrar y ejecutar con modelos calibrados. No son resultados ni equivalencia numérica con la librería oficial `ragas`.

Fuente metodológica: laboratorio aportado por el equipo `S10_Lab_Agentic_RAG_RAGAS_RESUELTO.ipynb`, bloque Lab C, celdas de faithfulness/context precision/context recall/answer relevancy. Se revisaron directamente sus definiciones antes de implementar.

| Métrica | Definición implementada |
|---|---|
| Faithfulness | Proporción de unidades de respuesta y explicación que el evaluador declara sustentadas por la evidencia efectiva; segmentación por frases/líneas preserva puntos de IDs y decimales |
| Context precision | Fracción de pasajes pertinentes a la pregunta y contrato, como S10; NO average precision ponderada por posición de otras implementaciones |
| Context recall | Veredicto binario de cobertura de referencia completa por toda la evidencia, como S10; NO promedio por afirmación de referencia |
| Answer relevancy | Generar pregunta a partir de respuesta y medir coseno con pregunta original mediante embeddings fijados; rango natural [-1,1], no reescalado para aparentar 0–1 |

Cambios de seguridad frente al ejemplo: no devolver faithfulness=1 para respuesta sin afirmaciones; veredicto JSON booleano estricto, no regex que confunda «sí» dentro de una negación; errores nulos, no notas por defecto; una evaluación parcial fallida invalida esa métrica del caso y conserva todos los juicios. Reintento solo de formato, máximo uno.

No respondibles: context precision/recall N/A porque no existe pasaje positivo que deba recuperarse. Abstenciones: answer relevancy N/A porque reconstruir pregunta desde una negativa genérica no mide adecuadamente pertinencia; faithfulness sí examina su formulación si hay respuesta. Casos respondibles con contexto vacío: recall=0 por definición y precision N/A. Respuesta vacía: faithfulness/relevancy N/A, nunca perfectas; el harness registra por separado fallo de salida y lo penaliza en su métrica automática. Todos los promedios deben mostrar total, válidos, errores y N/A.

En agente se usa el contexto EFECTIVAMENTE entregado, incluidos campos de herramienta, con operación/verificación disponible para faithfulness/recall. Se registran cantidad recuperada y cantidad efectiva; context precision de este paquete no aísla calidad del retriever. No ocultar esa diferencia.

Limitaciones: un juez pequeño puede aceptar contradicciones; segmentar frases no garantiza afirmaciones atómicas; el coseno puede ser alto pese a error factual; recall binario es menos granular. Los juicios requieren revisión, no constituyen verdad absoluta. Ninguna nota de referencia se devuelve al sistema ni a su juez general; solo context recall utiliza la referencia, como exige su definición.

Pendientes: fijar evaluador/embeddings y comprobar calibración, runner y exportación, ejecutar gold con configuración congelada, revisar originales y denominadores, reportar las cuatro métricas y sus límites. No afirmar que RAGAS está completado por existir este módulo.
