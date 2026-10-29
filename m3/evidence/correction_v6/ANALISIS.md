# V6: diagnóstico ejecutado, no candidato aprobado

Corrida del 29/10/2026, T4, 16:57–17:08 UTC. Notebook sin errores; 70 tests aprobados; hashes de fuentes coinciden con paquete v6; resumen de calibración recalculado exactamente. Revisión técnica asistida por IA, no revisión humana independiente. Originales preservados en esta carpeta.

Se reutilizaron contextos de desarrollo v5, sin reconstruir recuperación. No comparar sus latencias con RAG completo. No es gold final ni RAGAS.

## Hallazgos

- 30/32 salidas válidas (v5: 32/32); fallan los dos cálculos del control sin RAG por citas inventadas. Los intentos y errores se conservan.
- Avanzado/agente mantienen las cuatro modalidades correctas. Agente mantiene ambas diferencias exactas (75.233.920 y 226.596.000), pero no cita adecuadamente ambos operandos.
- Avanzado/agente mejoran abstención de cláusula. En auditoría dicen «No se concluyó una auditoría específica», afirmación que excede ausencia de informe en estas fuentes; no dar por validada abstención semántica.
- Controlador v6 empeora: las seis consultas sin necesidad de herramienta intentan llamarla y terminan por bloqueo de repetición. Los dos cálculos sí ejecutan correctamente. No adoptar ROUTER_V6 como sustituto del v5.
- 48/48 juicios tienen formato válido; 48/48 incumplen transcripción literal de la respuesta y copian fuentes. No se corrigió ninguna nota.
- Los 16 juicios sobre respuestas incorrectas (4 casos x 2 longitudes x 2 condiciones) reciben 1–2: mejora específica. A la vez penaliza hechos correctos y abstenciones válidas, incluso contradiciendo sus propias razones.
- Diferencia absoluta media de verbosidad antes/después: 1,50 / 1,167, máximo 3 en ambas; 6/12 y 4/12 pares superan un punto. La mitigación reduce parcialmente el efecto dentro de v6, pero queda peor que v5 después (0,833). Rango diagnóstico de respuestas breves: 10/12 antes, 8/12 después. No declarar juez fiable ni sesgo resuelto.

## Decisión

No adoptar v6 completa ni proclamar cierre de calidad. Conservar v5 y v6 como diagnósticos; no combinar resultados de distintas configuraciones como si fueran una corrida. Antes del gold se debe elegir y registrar una configuración única. Juez alternativo/calibración y revisión humana siguen pendientes. En paralelo se implementa el núcleo del harness con métricas explícitas y tests sin inferencia final, evitando bloquear todo el desarrollo en sucesivos cambios de prompts.
