# Rúbrica del juez ContractRisk v1.2

## Propósito

El juez evalúa si la salida de un sistema aplica correctamente la clasificación de suficiencia descriptiva contractual. No determina fraude, corrupción, ilegalidad ni riesgo jurídico sustantivo.

## Regla obligatoria

- Si la etiqueta del sistema coincide con la etiqueta esperada, solo puede asignarse 3, 4 o 5.
- Si las etiquetas son diferentes, solo puede asignarse 1 o 2.
- Una etiqueta correcta sin explicación recibe 4.
- Una etiqueta incorrecta sin explicación recibe 1.
- La extensión, el estilo y la seguridad verbal no aumentan el puntaje.

## Niveles

| Nivel | Descripción |
|---:|---|
| 5 | La etiqueta coincide con la referencia, la explicación aplica de forma concreta y correcta el criterio y no introduce afirmaciones incompatibles o no sustentadas. |
| 4 | La etiqueta coincide y no existe contradicción material, pero la explicación está ausente, es parcial o demasiado general. |
| 3 | La etiqueta coincide, pero la explicación contiene una ambigüedad o contradicción relevante; o la decisión correcta no puede extraerse con seguridad. |
| 2 | La etiqueta no coincide, pero la explicación reconoce parte del criterio, la ambigüedad o el carácter fronterizo. |
| 1 | La etiqueta no coincide y no existe justificación útil, el razonamiento contradice el criterio o no permite identificar una decisión válida. |

## Casos frontera y falsos negativos

La marca de frontera no modifica las anclas ni permite premiar una etiqueta incorrecta. Sirve para analizar separadamente textos cortos pero suficientes, textos largos pero vagos, perfiles sin actividad concreta, referencias circulares y otros casos ambiguos. Un falso negativo de `REQUIERE_REVISION` recibe 1 si carece de explicación útil y se registra además como una alerta omitida en la dimensión de dominio.

## Formato

El juez responde dos líneas:

```text
PUNTAJE=<nivel permitido>
RAZON=<justificación de máximo 40 palabras>
```

El formato no incluye un número de ejemplo para evitar anclar al modelo a un nivel particular.

## Sesgo controlado

Se reconoce la preferencia por verbosidad. Las salidas usan el mismo orden de campos, la explicación candidata se limita a 80 palabras y una prueba controlada compara versiones concisa y extensa de la misma decisión. La mitigación reduce la oportunidad de premiar longitud, pero no demuestra que el sesgo desaparezca en todos los casos.
