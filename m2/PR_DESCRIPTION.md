# Entrega M2: harness de evaluación de ContractRisk

## Resumen

- Incorpora un conjunto de evaluación nuevo, anotado por dos personas y consolidado en formato CSV y JSON.
- Implementa un harness reutilizable con tres dimensiones: Macro F1, LLM-as-a-judge y cumplimiento del dominio.
- Evalúa el baseline RoBERTalex + LoRA de M1 con una rúbrica versionada y una prueba de sesgo de verbosidad.
- Conserva predicciones, métricas, scorecard, comprobación de sesgo y metadatos verificables.
- Incluye un notebook reproducible para Google Colab y documentación de uso, resultados y limitaciones.

## Resultado final verificado

| Dimensión | Métrica | Resultado |
|---|---|---:|
| Automática | Macro F1 | 0.7333 |
| LLM-as-a-judge | Promedio (1–5) | 3.4 |
| Cumplimiento del dominio | Etiqueta correcta y juez >= 4 | 0.8000 |

Resultados complementarios: accuracy 0.8000, recall de `REQUIERE_REVISION` 0.4286, exactitud en casos frontera 0.5556 y exactitud en casos regulares 1.0000.

## Validación

- 20 casos únicos y 9 casos frontera/adversariales.
- Sin solapamiento por ID ni texto con train/validation de M1.
- Parser del juez, guardrails, métricas y ejecución controlada: 4 pruebas superadas.
- Notebook sin rutas locales y artefactos sin tokens ni secretos detectados.
- Hashes SHA-256 registrados para insumos y resultados finales.

## Lectura honesta

El baseline funciona bien en casos regulares, pero su recall de `REQUIERE_REVISION` es insuficiente para uso operativo autónomo. Los cuatro errores de clasificación se concentran en casos frontera. Por eso, el resultado debe entenderse como una línea base reproducible para comparar mejoras futuras, no como evidencia de que el sistema ya esté listo para decidir sin revisión humana.

## Alcance del PR

Este PR integra exclusivamente el trabajo de la entrega M2 desde la rama `Entrega/contractrisk-m2`. La rama `main` no se modifica hasta que el PR sea revisado y aprobado.
