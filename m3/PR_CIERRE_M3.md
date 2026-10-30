# Entrega M3: RAG, agente, evaluación y cierre documental

## Contenido

- Corpus público de 24 fichas, índice reconstruible y gold de 12 preguntas.
- Sin RAG, RAG ingenuo, híbrido con reranking, agente con herramienta y ablaciones.
- Corrida final conservada; harness 1.1 y RAGAS 1.1 sobre las respuestas guardadas.
- Reporte, ruta de reproducción y auditorías de resultados.
- Declaración de uso de IA aportada por los autores y constancia de privacidad.

## Verificaciones

- 128 pruebas aprobadas en el cierre local.
- Corpus congelado sin cambios; ninguna regeneración de respuestas ni notas del juez en el cierre documental.
- Auditoría anterior desde clon limpio: tablas, hashes, reconstrucción y enlaces (ver m3/REVISION_ENTREGA.md).
- Contraste con guía y salvedades en m3/CIERRE_REQUISITOS.md.

## Límites relevantes

No se declara sistema seguro para uso autónomo. Persiste abstención 0/2 en avanzado/final, errores de generación y del juez; RAGAS omite algunas afirmaciones cortas y su context precision del laboratorio resulta degenerada. Harness adaptado a QA y correcciones 1.1 post-hoc expresamente documentadas.

## Revisión y reproducción

Empezar por m3/README.md y m3/RUTA_ENTREGA.md. El notebook final reproduce 1.0; seguir después el recálculo harness 1.1 y el notebook RAGAS 1.1 para las tablas vigentes. No se realizó una nueva corrida integral T4 en este cierre CPU.

No fusionar sin aprobación del equipo. La entrega en Interactiva y su comprobante son pasos humanos separados.
