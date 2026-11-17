# Calibración Qwen 7B — ejecutada y rechazada para validar calidad

17/11/2026 06:05–06:12 UTC (01:05–01:12 Bogotá), Tesla T4. Código `18af8a620289f28e1b89b1bc5be0613206f608e5`, rúbrica `final-judge-candidate-1.1`. [ZIP original](original_results.zip), [notebook ejecutado](executed.ipynb), [auditoría](audit.json). Archivos conservados sin editar, ninguna nota sustituida.

Se verificaron CRC, ocho fuentes Python contra Git, notebook contra fuentes del commit, aprobación/anclas/configuración y recálculo idéntico del resumen. Cinco celdas ejecutables con salidas, cero salidas de error. Logs: 85 pruebas final y 128 M3 aprobadas. Ninguna generación alcanzó el límite de 320 tokens. El escaneo limitado de patrones de tokens no halló coincidencias; no es certificación absoluta de privacidad.

## Ejecución técnica

El kernel CUDA NF4 pasó. Qwen2.5-7B-Instruct cargó realmente 196 capas Linear4bit, sin offload CPU; cómputo FP16 y doble cuantización. Carga 247,22 s; memoria residente asignada 5.567.937.024 bytes y reservada 7.155.482.624 bytes. Son datos del juez, no un antes/después de eficiencia del generador contractual.

38/38 juicios con formato válido y sin ajuste de puntuaciones. Los logs confirman sincronización y cierre de [W&B mxxtuw0e](https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/mxxtuw0e). Dashboard/acceso externo no inspeccionados por el agente.

## Calidad del juicio: filtro no superado

| Condición previa | Resultado |
|---|---|
| Al menos 18/20 dentro de rango | 15/20 |
| Ningún caso malo recibe 4–5 | Cinco de diez casos malos reciben 4–5 |
| Diferencia mitigada máxima 1 por par | Dos pares difieren 3 puntos |

Falsos positivos: `short_bad` 5, `unjustified_abstention_bad` 5, `attribution_bad` 5, `empty_explanation_bad` 5 y `citation_bad` 4. Los diez casos buenos reciben 4–5, pero eso no compensa aceptar errores conocidos.

Hallazgos concretos de razones, no solo puntuaciones:

- Confunde Compraventa (tipo) con Mínima cuantía (modalidad), aunque ambos campos están disponibles.
- Justifica una abstención afirmando que falta la entidad, cuando sí está en el contexto.
- Aprueba una explicación que sitúa el monto en el objeto, aunque está en un campo distinto.
- Reconoce que la explicación está vacía pero le da 5, contraviniendo la regla explícita aprobada. Se conserva ese 5; no se aplica un cap automático.
- En `citation_bad` reconoce que la cita no respalda y aun así da 4. En `citation_good` su razón atribuye al sistema una cita que no eligió: incluso acertar el rango no garantiza buena razón.
- En `conflict_bad` detecta discrepancia y da 2, pero después supone sin sustento que la imagen debería mostrar el valor del snapshot. No puede decidir autenticidad por este paquete.

Verbosity: diferencia absoluta media antes 0,833 y después 1; máximo 3 en ambos. El rango permitido no se alcanzó. En un par malo la versión verbosa recibe una nota más adecuada pero la breve sigue indebidamente alta: la inestabilidad refleja también fallos de juicio, no solo preferencia por estilo. No afirmar que la mitigación funcionó ni que la longitud explica todos los errores.

No hay evidencia de que un parser corrupto, datos gold enviados al juez o truncamiento expliquen el fallo: formatos y hashes coinciden, no hay límite alcanzado y la whitelist excluye gold. Tampoco se ha comparado el mismo juez FP16/NF4: **no atribuir causalmente estos fallos a cuantización**.

## Decisión y continuación

`calibration_gate_passed=false` y `judge_validated_for_final=false` se conservan. Este juez no puede aprobar una caída máxima de calidad de la técnica eficiente. Los tests CPU prueban reglas/software, no calidad semántica.

[Segundo candidato](../../JUEZ_02.md): otra familia, misma rúbrica/anclas/parámetros compartidos y mismos umbrales. Los ejemplos conocidos son regresión, no una nueva validación ciega. Doce anclas de confirmación nuevas se fijan antes de observar el segundo candidato y no se ejecutan sin revisión humana. Aun si pasa la regresión, faltarán confirmación y auditoría de razones.
