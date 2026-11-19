# Rúbrica del juez final — versión final-judge-candidate-1.1

Transcripción legible de `RUBRIC` en [judge_final.py](judge_final.py), sin cambiar
el código o los criterios de las corridas. Se añade a la documentación porque
el paquete de revisión humana no incluía su texto completo. La regla de explicación
vacía ya estaba antes de las corridas; no se introduce después de ver las notas.

| Nota | Ancla literal del código |
|---|---|
| 1 | Respuesta inventada o esencialmente incorrecta; cifra central falsa, acusación sin evidencia o explicación que contradice el hecho central. |
| 2 | Error importante, explicación ausente o atribución falsa de evidencia; una cita existente no basta para respaldar lo afirmado. Sin explicación, nota máxima 2 aunque la respuesta corta sea correcta. |
| 3 | Respuesta parcialmente útil pero incompleta o con explicación/citas insuficientes para verificar una parte relevante. |
| 4 | Respuesta y explicación sustentadas y pertinentes, con citas verificables o abstención justificada; solo omisiones menores. |
| 5 | Respuesta completa y precisa para la pregunta, explicación verificable y citas pertinentes. Una abstención plenamente justificada puede merecer 5. |

La instrucción del juez también repite el máximo de 2 sin explicación y distingue
explicación ausente de explicación breve suficiente. El juez evalúa respuesta,
explicación y evidencia citada; no recibe el gold ni una comparación de aciertos.
No se recorta ni sustituye su nota por código: el parser conserva el puntaje crudo.

Control de longitud literal:

> No premies longitud, repetición, tono seguro ni estilo. Contenido y evidencia equivalentes deben recibir la misma nota; una respuesta breve puede ser completa.

Esto controla la nota de respaldo del contenido, no mide por separado fluidez,
usabilidad o calidad editorial. En los pares sintéticos se repiten frases cuatro
veces: no demuestra neutralidad ante toda explicación larga legítima. Se conserva
ese límite señalado por el revisor; no se cambian las notas para ocultarlo.

Huella de la rúbrica completa, sistema y control:
`88fa619df49d2db79f61e336312c6c38fe01b849763bec2b7a72c28b23648ec7`.
Fuente congelada usada en la calibración:
[commit 4c5d971](https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro/blob/4c5d971e95d4a3d6195c79c542154a8db2dcd6e0/final/judge_final.py).

La aceptación está limitada a la tarea/configuración documentada. No garantiza
juicio infalible, ni sustituye los controles humanos de errores críticos del dominio.
