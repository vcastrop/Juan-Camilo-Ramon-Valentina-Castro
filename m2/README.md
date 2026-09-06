# Harness de evaluación ContractRisk M2

El harness de ContractRisk evalúa si un sistema distingue descripciones contractuales suficientemente informativas de aquellas que necesitan revisión humana. Una buena respuesta asigna la etiqueta correcta, evita dejar pasar textos insuficientes y aplica el criterio contractual sin convertir la alerta en una acusación de fraude o ilegalidad.

## Eval set de dominio

El archivo `eval/contractrisk_m2_eval_gold.csv` contiene 20 contratos nuevos que no pertenecen a train ni validation de M1. Cada fila incluye input, etiqueta esperada, criterio específico y marca de caso frontera.

| Composición | Casos | Porcentaje |
|---|---:|---:|
| `SUFICIENTE` | 13 | 65 % |
| `REQUIERE_REVISION` | 7 | 35 % |
| Casos frontera | 9 | 45 % |

Dos anotadores evaluaron los 20 ejemplos de forma independiente. Coincidieron en 18 casos: 90 % de acuerdo y Cohen's Kappa 0,765. Los casos `m2_008` y `m2_012` se adjudicaron como `REQUIERE_REVISION`; el razonamiento y las anotaciones originales están en `evidence/`.

## Sistema evaluado

El baseline es el modelo de M1: `BSC-LT/RoBERTalex` adaptado con LoRA para clasificación binaria. El sistema devuelve `label`, `confidence` y un campo opcional `explanation`. El baseline M1 no genera explicación, por lo que ese campo queda vacío. `systems.py` implementa el adaptador y `harness.py` acepta cualquier sistema que respete la misma interfaz, pensando en sustituirlo por el RAG de M3.

## Dimensiones

### 1. Métrica clásica automática

Macro F1 asigna el mismo peso a `SUFICIENTE` y `REQUIERE_REVISION`. Es la métrica principal porque siete de los veinte casos pertenecen a la clase minoritaria y el accuracy por sí solo puede ocultar que el sistema deja escapar alertas.

### 2. LLM como juez

`Qwen/Qwen2.5-1.5B-Instruct` evalúa cada salida con la rúbrica versionada `rubrics/judge_rubric_v1_2.json`. El prompt muestra el texto, la etiqueta gold, el criterio gold y la salida normalizada. El parser acepta el formato etiquetado `PUNTAJE=` y `RAZON=`; si falla, intenta una reparación y deja registrada cualquier recuperación.

| Nivel | Ancla |
|---:|---|
| 5 | Etiqueta correcta y explicación concreta, correcta y sin afirmaciones no sustentadas. |
| 4 | Etiqueta correcta, pero explicación ausente, parcial o general. La longitud no aumenta el nivel. |
| 3 | Etiqueta correcta con una ambigüedad o contradicción relevante, o decisión correcta no extraíble con seguridad. |
| 2 | Etiqueta incorrecta, pero la explicación reconoce parte del criterio o la ambigüedad del caso. |
| 1 | Etiqueta incorrecta sin justificación útil o con razonamiento incompatible con el criterio. |

La regla objetiva permite 3-5 cuando las etiquetas coinciden y 1-2 cuando difieren. Como el baseline no produce explicaciones, un acierto se normaliza a 4 y un error a 1. `predictions_baseline.csv` conserva el puntaje bruto, el validado y si intervino esta salvaguarda.

### 3. Cumplimiento del dominio

`contract_review_utility` refleja que los dos tipos de error no cuestan lo mismo:

| Resultado | Utilidad |
|---|---:|
| Clasificación correcta | 1,0 |
| `SUFICIENTE` enviado innecesariamente a revisión | 0,5 |
| `REQUIERE_REVISION` dejado pasar | 0,0 |

La medida penaliza con mayor severidad un falso negativo porque deja pasar una descripción insuficiente sin alerta. También se reportan recall de `REQUIERE_REVISION` y accuracy en casos frontera.

## Scorecard del baseline

| Dimensión | Métrica | Resultado |
|---|---|---:|
| Métrica clásica | Macro F1 | 0,733 |
| LLM como juez | Promedio 1-5 | 3,400 |
| Cumplimiento del dominio | `contract_review_utility` | 0,800 |

Indicadores complementarios:

| Indicador | Resultado |
|---|---:|
| Accuracy | 0,800 |
| Precisión de `REQUIERE_REVISION` | 1,000 |
| Recall de `REQUIERE_REVISION` | 0,429 |
| F1 de `REQUIERE_REVISION` | 0,600 |
| Tasa de aprobación del juez, nivel >= 4 | 0,800 |
| Parsing exitoso del juez | 1,000 |
| Promedio bruto del juez en aciertos | 3,875 |
| Promedio bruto del juez en errores | 2,000 |
| Accuracy en casos frontera | 0,556 |
| Accuracy en casos regulares | 1,000 |

La matriz de confusión usa filas reales y columnas predichas en el orden `[REQUIERE_REVISION, SUFICIENTE]`:

```text
[[3, 4],
 [0, 13]]
```

## Lectura honesta

El baseline acertó 16 de 20 casos, pero solo detectó 3 de las 7 descripciones que requerían revisión. Los cuatro errores fueron falsos negativos y se concentraron íntegramente en los nueve casos frontera: `m2_003`, `m2_004`, `m2_008` y `m2_018`. No produjo falsos positivos, por lo que sus alertas fueron precisas, pero fue demasiado conservador al generarlas. El caso `m2_003`, “CONTRATO DE ARRIENDO 001 2020”, fue clasificado como suficiente con confianza 0,938 aunque no identifica el inmueble ni la finalidad, lo que demuestra que una confianza alta no garantiza una decisión segura. La dimensión más severa es el recall de `REQUIERE_REVISION` (0,429), y el contraste entre casos frontera (0,556) y regulares (1,000) muestra que la debilidad está en textos que aparentan especificidad mediante cargos, tipos contractuales o referencias internas sin describir realmente la actividad. En M3 se debe priorizar aumentar esta sensibilidad mediante recuperación de contexto contractual, ajuste de umbral o una regla de abstención para enviar casos inciertos a revisión.

## Sesgo del juez y mitigación

Se controló el sesgo de verbosidad, por el cual un juez puede favorecer una respuesta larga sin que sea más correcta. Todas las salidas usan el mismo esquema, las explicaciones se limitan a 80 palabras y la rúbrica indica expresamente que la longitud no aumenta el nivel. La prueba controlada presentó la misma decisión en versión concisa y verbosa: ambas recibieron 5, con diferencia absoluta 0. Este resultado respalda la mitigación para ese ejemplo, pero no demuestra que el sesgo haya desaparecido en cualquier texto.

Durante el desarrollo también se detectaron dos fallos del juez: el modelo de 0,5B violó las anclas y un ejemplo numérico del formato indujo respuestas constantes. Ambos pilotos se conservaron en `evidence/`, se excluyeron del scorecard y motivaron la rúbrica v1.2. En la corrida final, el puntaje bruto promedio fue 3,875 para aciertos y 2,000 para errores, por lo que el juez sí distinguió ambos grupos antes de aplicar la salvaguarda.

## Reproducción en Colab

1. Abra `ContractRisk_M2_Harness_Colab.ipynb` en Google Colab.
2. Seleccione GPU T4.
3. Ejecute las celdas en orden.
4. El notebook clona la rama, instala versiones fijadas, valida el eval set, ejecuta las pruebas y corre el harness.
5. La última celda descarga `contractrisk_m2_resultados.zip`.

También puede ejecutarse desde la raíz del repositorio:

```bash
pip install -r m2/requirements-m2.txt
python m2/test_harness.py
python m2/run_baseline.py
```

La semilla es 42. El scorecard se genera durante la ejecución y no contiene resultados anticipados escritos en el código.

## Archivos principales

- `ContractRisk_M2_Harness_Colab.ipynb`: ejecución completa en Colab gratuito.
- `harness.py`: función reutilizable y cálculo de las tres dimensiones.
- `systems.py`: adaptador del modelo M1.
- `run_baseline.py`: ejecución del baseline y exportación.
- `eval/contractrisk_m2_eval_gold.csv`: eval set congelado.
- `rubrics/judge_rubric_v1_2.json`: rúbrica final del juez.
- `results/scorecard_baseline.csv`: scorecard final.
- `results/predictions_baseline.csv`: evidencia fila por fila.
- `results/run_metadata.json`: modelos, semilla, entorno y hashes de la corrida final.
- `evidence/`: acuerdo humano, adjudicaciones y pilotos descartados del juez.

Fuente de los textos: [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/data_preview), Portal de Datos Abiertos de Colombia.
