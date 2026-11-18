# Mistral con entrada histórica — fallo conservado y defecto de tokenización detectado

18/11/2026 06:20–06:27 UTC (01:20–01:27 Bogotá), T4, código `6f6ade46c897ed83865e4af0450dbb6c37c8571e`. [ZIP original](original_results.zip), [notebook ejecutado](executed.ipynb), [auditoría](audit.json). No se editaron puntuaciones ni razones.

Se verificaron CRC, nueve fuentes contra Git, celdas contra notebook del commit, hashes de aprobación/anclas/configuración y recálculo exacto del resumen. Cinco celdas ejecutables sin salida de error. Ningún intento alcanzó el límite de tokens. Logs: 93 pruebas final y 128 M3 aprobadas. Escaneo acotado de patrones de credenciales sin coincidencias; no es auditoría absoluta de privacidad.

## Resultado de esa corrida

- 38/38 juicios interpretables, 11/20 en rango (mínimo 18).
- Ocho respuestas malas con notas altas: short, number, conflict, unjustified_abstention, attribution, empty_explanation, citation y negation.
- Diferencia de hasta 3 puntos por verbosidad después de mitigación, frente al máximo permitido de 1. No se admite porque la media sea menor que la de Qwen.
- Incluso razones con rango correcto son problemáticas: cuestiona la abstención ante fuentes contradictorias y añade en un caso bueno una insinuación de sobrecosto no afirmada por la respuesta.
- Carga NF4 real con 224 capas, 214,08 s; datos técnicos no prueban calidad ni son eficiencia del generador contractual. [W&B](https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/ooiibaal) con cierre/sincronización según log; dashboard/acceso externo no comprobados.

## Hallazgo posterior de implementación

El camino heredado renderiza chat con sus símbolos especiales y después tokeniza con la adición automática de símbolos habilitada. El tokenizer Mistral fijo agrega así un BOS adicional. La [reconstrucción CPU](../tokenization_cpu_01/diagnostic.json) de los 38 mensajes reproduce longitudes que coinciden con los registros originales; produce dos BOS iniciales, frente a uno de la plantilla nativa. Los 38 corregidos coinciden con los tokens nativos. Qwen no presenta esa diferencia en los 38 mensajes reconstruidos.

Esto confirma un defecto de preparación de entrada, **no cuánto explica las notas ni que corregirlo asegure buen juicio**. El diagnóstico no ejecutó modelos ni GPU. Por tanto, esta corrida no valida a Mistral, pero tampoco permite atribuir todos sus fallos exclusivamente al checkpoint o a NF4.

Se conserva como referencia confusa de formato. [Prueba controlada](../../MISTRAL_TOKENFIX.md): mismo checkpoint/rúbrica/anclas/umbral y parámetros, cambiando el añadido de tokens y verificando equivalencia nativa. Los resultados corregidos aún no existen; confirmación nueva y auditoría semántica seguirán pendientes si supera regresión.
