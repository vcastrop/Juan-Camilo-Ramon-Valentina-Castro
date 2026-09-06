# Acuerdo y adjudicación del eval set M2

## Alcance

El conjunto contiene 20 descripciones contractuales nuevas, distintas de los datos utilizados en la entrega M1. Dos personas anotaron todos los casos de manera independiente con las etiquetas `SUFICIENTE` y `REQUIERE_REVISION`. También justificaron cada decisión e identificaron posibles casos frontera.

## Resultado de la doble anotación

- Casos anotados: 20.
- Acuerdos: 18.
- Desacuerdos: 2.
- Acuerdo observado: 90 %.
- Acuerdo esperado por las distribuciones marginales: 57,5 %.
- Cohen's Kappa: 0,765.

El Kappa indica un acuerdo sustancial una vez descontada la coincidencia esperable por azar. Este resultado no elimina la necesidad de adjudicar los desacuerdos, pero respalda que la guía se aplicó de forma consistente en la mayoría de los casos.

## Casos adjudicados

### `m2_008`

- Anotador 1: `SUFICIENTE`.
- Anotador 2: `REQUIERE_REVISION`.
- Etiqueta definitiva: `REQUIERE_REVISION`.
- Decisión: la expresión “apoyo administrativo combinado y de oficina” y la dependencia indican un ámbito general, pero no concretan las actividades contratadas.

### `m2_012`

- Anotador 1: `SUFICIENTE`.
- Anotador 2: `REQUIERE_REVISION`.
- Etiqueta definitiva: `REQUIERE_REVISION`.
- Decisión: el perfil de tecnólogo en imágenes diagnósticas es identificable, pero la fórmula “actividades propias de su perfil” no describe tareas contractuales concretas.

## Composición del conjunto gold

- `SUFICIENTE`: 13 casos.
- `REQUIERE_REVISION`: 7 casos.
- Casos frontera: 9 de 20, equivalentes al 45 %.

Para conservar los ejemplos potencialmente difíciles, un registro quedó marcado como caso frontera cuando al menos uno de los dos anotadores seleccionó `SI`. Esta marca no altera la etiqueta gold; permite calcular por separado el desempeño general y el desempeño en casos frontera.

## Archivos

- `contractrisk_m2_eval_gold.csv`: conjunto definitivo que consumirá el harness.
- `contractrisk_m2_acuerdo_anotadores.csv`: comparación de etiquetas, criterios y marcas de frontera.
- `contractrisk_m2_resumen_acuerdo.json`: métricas de acuerdo y decisiones de adjudicación en formato estructurado.

Los archivos originales de cada anotador deben conservarse sin modificaciones como evidencia del proceso independiente.
