# ContractRisk Colombia

ContractRisk ayuda a analistas y auditores a priorizar contratos públicos cuya descripción no permite comprender claramente qué se está contratando.

**Integrantes:** Juan Camilo Ramón y Valentina Castro.

## Objetivo M1

El sistema recibe `descripcion_del_proceso` de SECOP II y produce una clasificación binaria:

- `SUFICIENTE` (`1`): permite comprender razonablemente el bien, servicio, actividad u obra principal.
- `REQUIERE_REVISION` (`0`): es genérica, incompleta o ambigua y exige consultar información adicional.

`REQUIERE_REVISION` no significa fraude, corrupción, ilegalidad ni contrato irregular; solo representa insuficiencia descriptiva textual. Los placeholders, vacíos y códigos sin contenido se registran como `DESCARTAR` durante la anotación y no ingresan al clasificador binario.

## Fuente y licencia

Los textos provienen de [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/data_preview), suministrado por la Agencia Nacional de Contratación Pública - Colombia Compra Eficiente. El conjunto tiene cobertura nacional, idioma español y actualización diaria. Se consultaron mediante la API Socrata únicamente `id_contrato`, `descripcion_del_proceso` y `tipo_de_contrato`, con límite de 100.000 filas.

Los datos del Portal Nacional de Datos Abiertos se publican bajo sus términos de reutilización y la licencia recomendada **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. Este proyecto atribuye la fuente como exige el portal: “Fuente: Portal de Datos Abiertos www.datos.gov.co”. La anotación y transformación deben conservar la atribución y las condiciones de compartir igual.

## Construcción y anotación

Se elaboró una guía que pregunta si el texto permite identificar razonablemente la acción y el objeto contractual sin información externa. `tipo_de_contrato` se utilizó para diversificar el muestreo, nunca para asignar la etiqueta.

1. Calibración inicial de 15 textos.
2. Piloto independiente de 50 contratos: acuerdo 100 %, Cohen's Kappa 1.000.
3. Ampliación con 650 contratos únicos y diversos.
4. Cada anotador recibió 275 casos exclusivos y 100 compartidos.
5. En los 100 compartidos hubo 87 acuerdos y 13 desacuerdos: 87 % de acuerdo y Kappa 0.683.
6. Los desacuerdos se adjudicaron aplicando la guía v1.1 y quedaron documentados.

El dataset final contiene 699 textos únicos:

| Etiqueta | Ejemplos | Porcentaje |
|---|---:|---:|
| SUFICIENTE | 544 | 77.8 % |
| REQUIERE_REVISION | 155 | 22.2 % |

El split estratificado usa semilla 42:

| Split | Total | SUFICIENTE | REQUIERE_REVISION |
|---|---:|---:|---:|
| Train | 559 | 435 | 124 |
| Validation | 140 | 109 | 31 |

No existe solapamiento de IDs ni textos entre train y validation.

## Modelo y decisiones técnicas

La tarea requiere comprender una secuencia completa y producir una clase, por lo que se eligió una familia **encoder** con preentrenamiento masked language modeling. Se comparó la tokenización de vocabulario contractual entre BETO, XLM-R base y `BSC-LT/RoBERTalex`.

Se seleccionó **RoBERTalex**, un RoBERTa especializado en español jurídico, porque su dominio es cercano a la contratación pública y su tamaño base cabe en Colab T4 mediante adaptación eficiente.

Configuración LoRA:

| Parámetro | Valor | Razón |
|---|---:|---|
| `r` | 8 | Capacidad moderada para un dataset pequeño |
| `lora_alpha` | 16 | Escala de adaptación `alpha/r = 2` |
| `lora_dropout` | 0.10 | Regularización |
| `target_modules` | `query`, `value` | Proyecciones de atención |
| `modules_to_save` | `classifier` | Entrenar y conservar la cabeza binaria |

Se entrenaron 887.042 parámetros de 126.866.692 (0.699 %). Trainer evaluó cada época, guardó el mejor Macro F1 y aplicó early stopping; el entrenamiento terminó después de siete épocas en una Tesla T4.

## Resultados

Macro F1 es la métrica principal porque pondera por igual ambas clases y evita que la mayoría `SUFICIENTE` oculte un rendimiento pobre en `REQUIERE_REVISION`.

| Modelo | Accuracy | Macro F1 |
|---|---:|---:|
| Clase mayoritaria | 0.779 | 0.438 |
| TF-IDF + Logistic Regression | 0.857 | **0.802** |
| RoBERTalex + LoRA | 0.857 | 0.749 |

El Transformer superó ampliamente el punto trivial, pero **no superó el baseline TF-IDF**: su delta de Macro F1 fue -0.053. La matriz de confusión de RoBERTalex fue:

| | Pred. revisión | Pred. suficiente |
|---|---:|---:|
| Real revisión | 14 | 17 |
| Real suficiente | 3 | 106 |

El modelo logra recall 0.972 en `SUFICIENTE`, pero solo 0.452 en `REQUIERE_REVISION`. Los 17 falsos negativos son el problema principal para un sistema de priorización.

## Ejemplos cualitativos

- Acierto `REQUIERE_REVISION`: “Apoyo a la gestión ... como auxiliar en enfermería dentro de la estrategia EBS”. El cargo y contexto no concretan una función.
- Acierto `SUFICIENTE`: “Mantenimiento de la infraestructura física del almacén municipal...”. Acción y objeto son explícitos.
- Fallo: “Servicios profesionales especializados para fortalecer actividades propias de la Superintendencia...”. El modelo predijo `SUFICIENTE`, aunque “actividades propias” no explica la actividad contratada.

## Sesgos y limitaciones

- La clase minoritaria representa 22.2 % del dataset.
- El muestreo fue enriquecido por tipos contractuales y textos potencialmente difíciles; no reproduce exactamente la distribución natural de SECOP II.
- La suficiencia es un juicio humano sujeto a casos frontera, aunque se utilizó guía, doble anotación y Kappa.
- El modelo jurídico fue preentrenado principalmente con español legal general, no específicamente con contratación pública colombiana.
- Los textos SECOP pueden estar truncados, contener errores ortográficos o fórmulas institucionales repetitivas.
- El sistema no debe utilizarse para acusar irregularidades ni reemplazar la revisión humana.

## Reproducción en Colab

1. Abrir `ContractRisk_M1_FineTuning_LoRA_Colab_Ejecutado.ipynb`.
2. Seleccionar GPU T4.
3. Ejecutar las celdas en orden.
4. Cuando se solicite, subir `contractrisk_train.csv` y `contractrisk_validation.csv`.
5. El notebook instala dependencias fijadas, entrena, evalúa y exporta el adapter y resultados.

Para reproducir exactamente el split congelado desde el dataset consensuado:

```bash
python prepare_dataset.py
```

El adapter entrenado está incluido como `model/contractrisk_robertalex_lora_adapter.zip`. Aunque la descarga original de Colab conservó `roberta_bne` en el nombre, `adapter_config.json` confirma que su modelo base es `BSC-LT/RoBERTalex`; el archivo de entrega fue renombrado para evitar ambigüedad.

Dependencias principales: Python 3, PyTorch, Transformers 4.48.1, Datasets 3.2.0, PEFT 0.14.0, Accelerate 1.2.1 y scikit-learn 1.5.2.

## Integración futura

Este M1 aporta la señal de calidad descriptiva de ContractRisk. En el proyecto final puede combinarse con indicadores estructurados del contrato, recuperación de información y visualizaciones para priorizar revisión humana. El siguiente experimento debe buscar mayor recall de `REQUIERE_REVISION` mediante pérdida ponderada, ajuste de umbral, más ejemplos minoritarios o comparación con BETO.
