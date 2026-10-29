# ContractRisk M3: preguntas sobre contratos con fuentes

Este componente ayudará a consultar información pública de contratación y explicar sus respuestas con fuentes verificables. No determina por sí solo si un contrato es irregular.

**Estado: en construcción.** Todavía no existe una corrida de RAG ni resultados M3. La entrega histórica de M2 permanece intacta.

## Ruta y evidencia disponibles

Prueba inicial: `ContractRisk_M3_Prueba_RAG_Colab.ipynb` y `run_smoke.py`. Implementan índice denso Chroma y generación Qwen sobre cuatro preguntas de desarrollo. Trece pruebas locales aprobadas; inferencia real y compatibilidad de dependencias pendientes de Colab. No hay scorecard nuevo. Se generan chunks de 280 caracteres para esta prueba y se comprueba el límite real del tokenizer, sin truncamiento silencioso. La propuesta exploratoria de 800 caracteres permanece como evidencia, no como configuración final. Las revisiones de modelos se resuelven y registran durante esta primera corrida; después deben fijarse para la comparación definitiva.

Referencias técnicas consultadas: [Chroma, incorporación de embeddings](https://docs.trychroma.com/docs/collections/add-data), [modelo de embeddings del curso](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2), [generador Qwen](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct). Los tests con dobles sintéticos verifican el flujo, no la calidad de estos modelos.

- [Gold QA v1 revisado](eval/gold_v1/eval_set.json): 12 casos, revisión de Juan Camilo Ramon Perez del 28/10/2026 y corrección condicionada incorporada en m3_004. [Evidencia original](eval/gold_v1/evidence/REVISION_HUMANA_QA.md) preservada byte por byte; hashes en su manifiesto. El borrador anterior permanece intacto.
- [Fragmentación inicial](indexing/manifest.json): 24 fichas, 40 chunks, máximo 800 caracteres y solapamiento objetivo de 100 caracteres, con cortes preferentes por líneas/palabras. Es configuración inicial, no óptima demostrada. No es todavía un índice vectorial.
- Diez pruebas locales aprobadas: integridad, revisión, referencias y cobertura completa del texto bajo dos tamaños de fragmentación. No prueban calidad de inferencia ni funcionamiento en Colab.

La revisión humana del gold ya no está pendiente. El siguiente bloque técnico es construir embeddings/Chroma, el generador y el RAG ingenuo, seguido del evaluador corregido y su calibración. No se usarán preguntas gold para ajustar prompts o escoger configuraciones por sus resultados finales.

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
