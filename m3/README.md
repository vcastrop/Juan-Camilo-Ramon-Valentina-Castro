# ContractRisk M3: preguntas sobre contratos con fuentes

Este componente ayudará a consultar información pública de contratación y explicar sus respuestas con fuentes verificables. No determina por sí solo si un contrato es irregular.

**Estado: en construcción.** Todavía no existe una corrida de RAG ni resultados M3. La entrega histórica de M2 permanece intacta.

## Ruta y evidencia disponibles

- [Checklist completa](CHECKLIST.md): requisitos, correcciones de M2 y condiciones de cierre.
- [Decisiones iniciales](DECISIONES_INICIALES.md): alcance, materiales del curso, comparación adaptada y tareas humanas pendientes.
- [Corpus candidato](corpus/README.md): 24 fichas reales, fuente y límites.
- [Snapshot](corpus/source_snapshot.json), [documentos](corpus/documents.jsonl) y [manifiesto](corpus/manifest.json): trazabilidad y hashes.
- [Preparación reproducible](prepare_corpus.py) y [pruebas](tests/test_corpus.py).

Las diapositivas y notebooks privados del curso se usaron como referencia y no se incorporaron ni publicaron en este repositorio. Los ejemplos educativos y sus cifras ilustrativas no se presentan como datos ni resultados de ContractRisk.

## Próximo bloque

1. Revisar las fichas y redactar un conjunto de preguntas QA con referencias y criterios para revisión humana, separado de desarrollo/calibración.
2. Construir ingestión, fragmentación e índice, RAG ingenuo y evaluador corregido.
3. Medir fallos de desarrollo, implementar dos técnicas avanzadas y herramienta, ejecutar comparación y RAGAS en Colab T4, analizar y documentar la corrida real.

W&B y DSPy no bloquean este alcance: son extras del material. Todos los mínimos de la guía y las correcciones del profesor siguen en la checklist.

## Uso de IA

ChatGPT/Codex asistió en la inspección de materiales, planificación y programación inicial. El equipo proporcionó materiales y requisitos. La revisión humana de corpus, código y gold QA está pendiente y no se declara como realizada. El detalle inicial está en [Decisiones](DECISIONES_INICIALES.md#uso-de-ia-durante-esta-preparación).
