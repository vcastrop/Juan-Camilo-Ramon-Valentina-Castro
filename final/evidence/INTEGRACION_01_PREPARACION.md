# Preparación de integración 01

Fecha: 16/11/2026. Estado: lista para ensayo T4, no inferencia aprobada.

- Se preservan modelos, código y resultados M1–M3.
- Nuevos adaptadores: clasificador con base/revisión fija y adaptador M1; generador M3 y recuperación/herramienta reutilizados; VLM Qwen2-VL-2B con revisión fija consultada al Hub.
- Capa nueva de fichas completas y controles, con versión `final-integration-dev-0.1`; no atribuirle cifras históricas.
- 18 pruebas CPU en final/tests y 128 pruebas M3 aprobadas.
- Todos los archivos Python final y celdas de código del notebook compilan.
- Generadas cuatro imágenes de desarrollo en total: dos fichas representadas desde el snapshot, una transformación de contraste y una imagen vacía. La revisión visual local de una ficha confirmó legibilidad tras sustituir fallback de fuente que no representaba bien tildes. Se usa fuente Unicode y se registra origen/fuente/hash.
- Las imágenes no son capturas reales ni referencias humanas finales. No satisfacen todavía el mínimo visual final revisado.
- No se instalaron ni ejecutaron modelos ML localmente: T4 real pendiente. Tampoco se sustituyó el Space funcionando.
- El runner finaliza la run W&B en finally; no se alteró retrospectivamente la run de infraestructura marcada Crashed.
- Protocolo de memoria explícito: VLM separado del generador; respuesta multimodal desde lectura guardada, no benchmarking punta a punta.

El resultado de la corrida puede fallar en dependencias, carga, extracción o generación. Guardar evidencia completa, no renombrar éxito técnico como calidad y no modificar respuestas manualmente.
