# ContractRisk M3: preguntas sobre contratos con fuentes

Este componente ayudará a consultar información pública de contratación y explicar sus respuestas con fuentes verificables. No determina por sí solo si un contrato es irregular.

**Estado: en construcción, con comparación de desarrollo ejecutada.** Hay resultados reales de RAG, pero no scorecard final de M3. La entrega histórica de M2 permanece intacta.

## Estado vigente

Corrección candidata v4 preparada: [cambios y explicación de fallos](CORRECCIONES_V4.md), [notebook v4](ContractRisk_M3_Desarrollo_v4_Colab.ipynb). 50 pruebas locales pasan, incluidas regresiones con trazas reales v3. No hay resultados de inferencia v4 todavía; no se declara resuelto el error semántico por modificar un prompt.

Última ejecución real: [desarrollo v3](evidence/development_v3/ANALISIS.md), completada en T4, pero solo 18/32 salidas pasan el esquema. La herramienta calcula bien dos diferencias; el generador falla al presentarlas. Persisten llamadas innecesarias e invención de una conclusión de auditoría. Requiere corrección y nueva prueba antes del cierre. Las notas anteriores siguientes describen la preparación de esa corrida, no una validación de calidad.

Agente v3 implementado y probado localmente: [herramienta, límites y prueba preparada](AGENTE_DESARROLLO.md), [notebook Colab](ContractRisk_M3_Desarrollo_v3_Agente_Colab.ipynb). 33 pruebas locales pasan; no son evidencia de calidad de decisiones del modelo. Pendiente ejecución real del agente, juez independiente, RAGAS y comparación final. El prompt v3 candidato conserva v2 sin sobrescribirlo.

[Corrida de desarrollo v2, notebook y diagnóstico](evidence/development_v2/ANALISIS.md): denso 0/4, híbrido con filtro ID 3/4, híbrido con filtro ID y reranking 3/4 respuestas correctas. El reranking recuperó evidencia en 4/4, pero el generador confundió tipo y modalidad en un caso. 15/15 salidas válidas en formato; abstención correcta solo probada con contexto vacío. Gold humano de 12 casos congelado. Agente, juez corregido, RAGAS y evaluación final pendientes. Véase [checklist vigente](CHECKLIST.md).

Las notas de preparación siguientes son históricas; «pendiente» en ellas describe aquel hito, no reemplaza este estado.

## Ruta y evidencia disponibles

Actualización tras la primera corrida real: [diagnóstico y evidencia](evidence/smoke_dense_v1/ANALISIS.md). SQLite resuelto en Colab mediante backend alternativo, pero recuperación 0/4 contratos y salida inválida 4/4. Se preparó `run_development_v2.py` para comparar denso, híbrido con filtro explícito de ID y el mismo híbrido con reranking. El prompt v2 es común, sin autocorrección de respuestas. La nueva comparación aún requiere ejecución real. El guard de SQLite se integra antes de importar Chroma, y registra backend y versión.

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

ChatGPT/Codex asistió en la inspección de materiales, planificación y programación inicial. El equipo proporcionó materiales y requisitos. El gold QA fue revisado por Juan Camilo Ramon Perez según la evidencia preservada. No se afirma una revisión humana completa del código ni de los juicios finales pendientes. El detalle inicial está en [Decisiones](DECISIONES_INICIALES.md#uso-de-ia-durante-esta-preparación).
