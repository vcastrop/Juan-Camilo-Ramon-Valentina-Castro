# Proyecto integrador STAI — Definición de ContractRisk Colombia

Este documento completa la plantilla de definición del proyecto integrador con base en el corpus procesado, el protocolo de anotación, los baselines reproducibles y el fine-tuning de RoBERTalex mediante LoRA desarrollados para M1.

## 0 · Equipo

- **Nombre del equipo:** ContractRisk Colombia.
- **Integrantes:** Juan Camilo Ramón Pérez y Valentina Castro.
- **Correos:** jcramonp@eafit.edu.co // vcastrop1@eafit.edu.co .
- **Integrante de contacto con el profesor:** por confirmar por el equipo.
- **Coordinación del código:** GitHub, repositorio [Juan-Camilo-Ramon-Valentina-Castro](https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro) .
- **Reunión semanal fuera de clase:** Jueves 2:00 pm.

## 1 · Tema y proyecto

### ¿Qué es el proyecto en una frase?

ContractRisk Colombia es un sistema de clasificación de texto que ayuda a analistas y auditores a priorizar descripciones de contratos públicos de SECOP II que no contienen información suficiente para comprender razonablemente qué se está contratando.

La salida tiene dos clases:

- `SUFICIENTE`: la descripción permite identificar razonablemente qué se contrata y cuál es su objeto principal.
- `REQUIERE_REVISION`: la descripción es demasiado genérica, incompleta o ambigua y requiere que una persona consulte información adicional.

La etiqueta `REQUIERE_REVISION` no implica fraude, corrupción ni irregularidad. Es únicamente una señal textual de insuficiencia descriptiva.

### ¿Por qué este tema?

La contratación pública genera grandes volúmenes de información y un auditor no puede revisar manualmente todos los contratos con la misma profundidad. El proyecto busca convertir texto administrativo real en una señal de priorización comprensible y verificable, manteniendo siempre la decisión final en manos humanas. Además, permite trabajar con un problema colombiano concreto y con lenguaje contractual auténtico.

## 2 · Usuario y decisión

### ¿Quién usaría este sistema?

El usuario principal sería un analista de contratación pública, auditor o integrante de un equipo de control que revisa descripciones contractuales publicadas en SECOP II. Es una persona con conocimiento administrativo o jurídico que necesita decidir rápidamente qué registros merecen una revisión documental adicional.

### ¿Qué decisión o tarea concreta resuelve?

El sistema ayuda a priorizar contratos para revisión humana. Para cada descripción, genera una de dos recomendaciones:

1. `SUFICIENTE`: el objeto puede comprenderse razonablemente con el texto disponible.
2. `REQUIERE_REVISION`: la descripción no concreta suficientemente el bien, servicio, actividad u obra y conviene abrir documentos adicionales.

No reemplaza una auditoría ni determina legalidad. Reduce el espacio inicial de búsqueda y organiza la carga de revisión.

### ¿Qué hace actualmente la persona sin el sistema?

Sin el sistema, el analista debe leer las descripciones una por una, aplicar su propio criterio y abrir documentos adicionales cuando el texto parece genérico. Esta línea base humana consume tiempo, puede variar entre personas y dificulta priorizar de manera homogénea conjuntos grandes de contratos.

## 3 · Tarea central del modelo (M1)

### Tipo de tarea

Clasificación binaria supervisada de texto en español.

### Input y output

- **Input:** contenido de `descripcion_del_proceso` de un contrato de SECOP II.
- **Output numérico:** `0` para `REQUIERE_REVISION` y `1` para `SUFICIENTE`.
- **Output legible:** etiqueta textual y, en una aplicación posterior, una señal de prioridad para el auditor.

Antes de la clasificación se descartan registros sin texto analizable, como cadenas vacías, placeholders o valores compuestos únicamente por números o códigos. Estos registros no se convierten artificialmente en ejemplos de `REQUIERE_REVISION`.

### Modelo base candidato y selección

Se compararon tres encoders candidatos:

| Modelo | Alcance | Consideración |
|---|---|---|
| `BSC-LT/RoBERTalex` | Español jurídico | Dominio cercano al lenguaje contractual y administrativo. |
| `dccuchile/bert-base-spanish-wwm-cased` | Español general | BETO con whole-word masking. |
| `FacebookAI/xlm-roberta-base` | Multilingüe | Capacidad multilingüe innecesaria para un corpus solo en español. |

Se eligió `BSC-LT/RoBERTalex`, un encoder de la familia RoBERTa preentrenado en español jurídico. La comparación auxiliar de tokenización sobre seis expresiones contractuales produjo una fragmentación media de 3,33 subtokens para RoBERTalex, 4,00 para BETO y 4,67 para XLM-R. Esta evidencia no demuestra por sí sola superioridad predictiva, pero complementa la selección de este modelo junto a demas caracteristicas que presentaba a favor como idioma español, dominio de lenguaje juridico y viabilidad computacional.

El ajuste se realizó mediante LoRA sobre las proyecciones `query` y `value`, con `r=8`, `alpha=16`, `dropout=0.10` y conservación de la cabeza `classifier`. Se entrenaron 887.042 de 126.866.692 parámetros, aproximadamente el 0,699 % del modelo.

## 4 · Dataset

### Fuente del texto

Los textos proceden del conjunto abierto [SECOP II — Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/data_preview), publicado en el portal Datos Abiertos Colombia. Se conservaron como variables principales `id_contrato` y `descripcion_del_proceso`, junto con metadata auxiliar como `tipo_de_contrato` para exploración y diversidad de muestreo. La metadata no se utilizó para decidir la etiqueta.

### Proceso de anotación

Las etiquetas se construyeron manualmente porque SECOP II no incluye una etiqueta preparada para esta tarea específica.

- Se redactó una guía de anotación para distinguir `SUFICIENTE`, `REQUIERE_REVISION` y `DESCARTAR`.
- En un piloto independiente de 50 contratos hubo 100 % de acuerdo y Cohen's Kappa de 1,000.
- La ampliación reunió 650 contratos únicos y diversos.
- Cada anotador recibió 275 casos exclusivos y 100 casos compartidos.
- En los 100 compartidos hubo 87 acuerdos y 13 desacuerdos: 87 % de acuerdo y Kappa de 0,683.
- Los desacuerdos se adjudicaron aplicando la guía v1.1 y se conservaron como evidencia del proceso.
- Después de eliminar descartes y resolver los casos finales, se obtuvieron 699 textos únicos utilizables.

### Tamaño y partición

- **Total:** 699 ejemplos.
- **Entrenamiento:** 559 ejemplos.
- **Validación:** 140 ejemplos.
- **Distribución total:** 544 `SUFICIENTE` y 155 `REQUIERE_REVISION`.
- **Entrenamiento:** 435 `SUFICIENTE` y 124 `REQUIERE_REVISION`.
- **Validación:** 109 `SUFICIENTE` y 31 `REQUIERE_REVISION`.
- **Split:** estratificado con semilla 42.
- **Control de fuga:** no hay IDs ni textos duplicados entre entrenamiento y validación.

### Idioma

Español, con vocabulario administrativo, jurídico y contractual propio de entidades públicas colombianas.

### Licencia y condiciones de uso

La fuente se publica en el portal oficial de Datos Abiertos Colombia. Antes de redistribuir una copia completa del corpus original debe verificarse y conservarse la licencia y metadata vigentes indicadas en la ficha oficial. El repositorio del proyecto contiene únicamente las muestras y particiones necesarias para reproducir el ejercicio académico, y debe mantener atribución a SECOP II y Datos Abiertos Colombia.

### Sesgos y limitaciones conocidas

- Solo 155 de 699 ejemplos pertenecen a `REQUIERE_REVISION`.
- El muestreo fue enriquecido por tipos contractuales y posibles casos difíciles, por lo que no reproduce necesariamente la distribución natural completa de SECOP II.
- Las etiquetas dependen de una guía humana y existen casos frontera entre profesión o área mencionada y actividad contractual concreta.
- El acuerdo Kappa de 0,683 en la ampliación muestra consistencia sustancial, pero también ambigüedad real.
- RoBERTalex fue preentrenado en español jurídico general, no específicamente en descripciones SECOP colombianas.
- La partición de validación también se utilizó para seleccionar el mejor checkpoint y aplicar early stopping; no equivale a un test final completamente independiente.

## 5 · Métrica de éxito

### Métrica principal y métricas secundarias

- **Principal:** Macro F1.
- **Secundarias:** accuracy, Macro Precision, Macro Recall, métricas por clase y matriz de confusión.

### ¿Por qué Macro F1?

Las clases están desbalanceadas: 109 de los 140 ejemplos de validación son `SUFICIENTE`. La accuracy puede parecer alta aunque un sistema ignore por completo `REQUIERE_REVISION`; el baseline mayoritario obtuvo accuracy 0,779 sin detectar ninguna de las 31 revisiones. Macro F1 calcula el F1 de cada clase y les asigna el mismo peso, por lo que refleja mejor el desempeño sobre la clase minoritaria.

En el uso previsto también se presta atención especial al recall de `REQUIERE_REVISION`, porque un falso negativo representa una descripción insuficiente que el sistema dejaría pasar sin alerta.

### Baselines razonables

Se implementaron dos baselines funcionales y reproducibles sobre las mismas 140 filas de validación:

1. **Clase mayoritaria:** siempre predice `SUFICIENTE`. Obtuvo accuracy 0,779 y Macro F1 0,438.
2. **TF-IDF + regresión logística:** utiliza unigramas y bigramas, `min_df=2`, máximo 10.000 características y pesos balanceados. Obtuvo accuracy 0,886 y Macro F1 0,838.

### Resultado del modelo ajustado

RoBERTalex + LoRA obtuvo:

- Accuracy: 0,879.
- Macro Precision: 0,883.
- Macro Recall: 0,749.
- Macro F1: 0,790.
- Matriz de confusión: `[[16, 15], [2, 107]]`, con orden `[REQUIERE_REVISION, SUFICIENTE]`.

El modelo superó ampliamente el baseline trivial, demostrando aprendizaje real, pero quedó 0,048 puntos de Macro F1 por debajo de TF-IDF. Detectó 16 de 31 revisiones y dejó escapar 15; en cambio, reconoció 107 de 109 textos suficientes. Su comportamiento fue conservador: cuando emitió una alerta de revisión normalmente tuvo razón —precisión 0,889—, pero generó pocas alertas para esa clase —recall 0,516—.

El mejor checkpoint apareció en la época 3 con Macro F1 0,789734. En las épocas 4 y 5 descendió a 0,765886; early stopping detuvo el proceso y `load_best_model_at_end=True` restauró el checkpoint de la época 3.

## 6 · Componente visual (M4) — plan inicial

### Integración propuesta

El componente visual puede ser un panel para auditores que muestre:

- Distribución de contratos clasificados como `SUFICIENTE` y `REQUIERE_REVISION`.
- Lista priorizada de alertas con descripción, ID y metadata contractual.
- Matriz de confusión y métricas por clase para transparentar el desempeño.
- Resaltado de términos o fragmentos relevantes como apoyo explicativo, aclarando que no constituyen una justificación jurídica.
- Filtros por tipo de contrato, entidad, fecha u otra metadata disponible.
- Vista de revisión humana para confirmar o corregir la sugerencia del modelo.

### Imágenes o prototipos representativos

Se pueden diseñar tres vistas iniciales:

1. **Resumen ejecutivo:** tarjetas de cantidad de contratos, porcentaje de alertas y distribución por clase.
2. **Bandeja de revisión:** tabla ordenable con ID, descripción resumida, predicción y prioridad.
3. **Detalle del contrato:** texto completo, explicación de la etiqueta, metadata y acción humana de confirmar o corregir.

Este plan es inicial y puede modificarse después de validar necesidades reales de los usuarios y requisitos de M4.

## 7 · Riesgos éticos y de uso

### ¿Quién podría salir perjudicado si el sistema falla?

- Auditores y analistas, si confían excesivamente en una clasificación incorrecta.
- Entidades públicas o contratistas, si una alerta textual se interpreta equivocadamente como sospecha de fraude.
- La ciudadanía, si descripciones insuficientes relevantes quedan sin revisión debido a falsos negativos.
- Equipos de control, si demasiadas falsas alertas desvían recursos limitados.

### ¿En qué grupos o casos podría fallar más?

- Tipos contractuales poco representados en el conjunto anotado.
- Descripciones con lenguaje técnico, regional o institucional diferente al observado en entrenamiento.
- Casos frontera que mencionan profesión y contexto, pero no una actividad concreta.
- Textos formalmente largos que parecen informativos, aunque no especifiquen el alcance contractual.
- Entidades o periodos posteriores con cambios de estilo en la redacción.

No hay evidencia suficiente para afirmar diferencias de desempeño entre grupos demográficos, porque el dataset y la tarea no fueron diseñados para medirlas.

### Mitigaciones

- Mantener revisión humana y presentar la salida como recomendación, no como decisión automática.
- Mostrar explícitamente que `REQUIERE_REVISION` no significa fraude, corrupción ni ilegalidad.
- Priorizar la mejora del recall de la clase minoritaria mediante más ejemplos, pérdida ponderada, sobremuestreo solo en entrenamiento y estudio del umbral de decisión.
- Evaluar futuras versiones sobre un conjunto de test independiente.
- Monitorear resultados por tipo de contrato y otras categorías pertinentes.
- Conservar trazabilidad de dataset, guía, versión del modelo, semilla, métricas y predicciones.
- Permitir correcciones humanas y utilizarlas únicamente mediante un protocolo controlado de actualización.

## Recursos del proyecto

- [Repositorio de GitHub](https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro)
- [Fuente SECOP II — Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/data_preview)
