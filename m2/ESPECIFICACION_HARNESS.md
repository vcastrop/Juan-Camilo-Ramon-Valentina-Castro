# Especificación del harness ContractRisk M2

## Qué evalúa

El harness mide si un sistema identifica correctamente descripciones contractuales que no permiten comprender con suficiente precisión qué se está contratando. Una buena salida asigna una de las dos etiquetas permitidas, evita dejar pasar descripciones insuficientes y, cuando ofrece una explicación, aplica el criterio del caso sin inventar señales de fraude o ilegalidad.

## Contrato de entrada

Cada ejemplo del eval set contiene:

- `eval_id`: identificador estable del caso.
- `id_contrato`: identificador de trazabilidad en SECOP II.
- `descripcion_del_proceso`: único texto que recibe el sistema evaluado.
- `expected`: etiqueta gold.
- `criterio_gold`: razón específica que sustenta la etiqueta.
- `caso_frontera`: `SI` o `NO`.

El campo `tipo_de_contrato` se conserva como metadata descriptiva y no se entrega al clasificador para decidir la etiqueta.

## Contrato del sistema

El harness recibe una función o adaptador con esta interfaz conceptual:

```python
def sistema(texto: str) -> dict:
    return {
        "label": "SUFICIENTE" | "REQUIERE_REVISION",
        "confidence": float | None,
        "explanation": str | None,
    }
```

Esto permite evaluar ahora el clasificador RoBERTalex + LoRA de M1 y sustituirlo posteriormente por otro sistema, incluido el RAG de M3, sin cambiar el eval set ni las métricas.

## Dimensión 1: métrica clásica automática

La métrica principal es **Macro F1**. Se calcula el F1 de cada clase y luego se promedian ambos valores con el mismo peso. Esta elección evita que la mayoría `SUFICIENTE` oculte un rendimiento deficiente en `REQUIERE_REVISION`. También se reportan accuracy, precisión, recall y F1 por clase, pero no reemplazan la métrica principal.

## Dimensión 2: LLM como juez

El juez predeterminado es `Qwen/Qwen2.5-0.5B-Instruct`, un modelo instruct abierto y suficientemente pequeño para Colab gratuito. Recibe el texto contractual, la etiqueta gold, el criterio gold y la salida normalizada del sistema. Devuelve exclusivamente un puntaje entero de 1 a 5 y una justificación breve conforme a `rubrics/judge_rubric_v1.json`.

El analizador acepta JSON directo o dentro de un bloque de código. Si la primera respuesta no puede analizarse, solicita una reparación en formato JSON. Tras dos respuestas inválidas aplica un respaldo determinista coherente con la rúbrica y registra `judge_parse_ok=False`; por eso el scorecard informa también la tasa de análisis exitoso y no oculta fallos del juez.

Los indicadores de esta dimensión serán:

- promedio del puntaje 1–5;
- porcentaje de casos con puntaje mayor o igual a 4;
- porcentaje de respuestas del juez que pudieron analizarse sin recurrir a un valor de respaldo.

## Dimensión 3: utilidad de revisión contractual

La medida propia del dominio asigna utilidad por caso:

| Resultado | Utilidad |
|---|---:|
| Clasificación correcta | 1,0 |
| Texto `SUFICIENTE` enviado innecesariamente a revisión | 0,5 |
| Texto `REQUIERE_REVISION` dejado pasar como suficiente | 0,0 |

El promedio se denomina `contract_review_utility`. La asimetría refleja el objetivo operativo: un falso positivo consume revisión humana, mientras que un falso negativo deja pasar una descripción insuficiente sin alerta. Junto con esta utilidad se reportan el recall de `REQUIERE_REVISION` y el desempeño separado en casos frontera.

## Control del sesgo del juez

Se reconoce el sesgo de verbosidad: algunos jueces tienden a favorecer respuestas largas aunque no sean más correctas. La mitigación consta de cuatro controles versionados:

1. todas las salidas se presentan con el mismo esquema;
2. las explicaciones se normalizan y se limitan a 80 palabras;
3. la rúbrica indica que la longitud no otorga puntaje;
4. el harness compara una respuesta correcta concisa con otra artificialmente verbosa y reporta la diferencia del juez.

## Reproducibilidad

- Semilla global: `42`.
- Eval set congelado: `eval/contractrisk_m2_eval_gold.csv`.
- Rúbrica versionada: `rubrics/judge_rubric_v1.json`.
- Modelo evaluado por defecto: adapter LoRA M1 sobre `BSC-LT/RoBERTalex`.
- Juez por defecto: `Qwen/Qwen2.5-0.5B-Instruct`.
- El harness no contiene métricas esperadas escritas manualmente; todos los resultados deben provenir de la ejecución.
