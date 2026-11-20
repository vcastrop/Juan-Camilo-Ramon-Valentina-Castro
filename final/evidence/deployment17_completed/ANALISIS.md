# Despliegue 17 completado — técnica funcional, límite visual comprobado

Originales conservados sin modificar:

- ZIP `original_results.zip`: SHA256 `7a9146dfa7a3fc6eccf36a727438d7f2a9c5ee4f3ad4723c8b23170fc8c1c72d`.
- Notebook `executed.ipynb`: SHA256 `30c612200f732c0a92aabae128056228985d5a9125756abd4011e7ab2d7db09a`.
- Código `c966f0aee507fab70d349a9d385445287952c5ce`.
- Payload SHA256 `145fe12404de1c90615b4809303a10e208443f2fc14658d1c5ca9e1e418a3ce8`.

Se verificaron los hashes de miembros y el vínculo app/payload; los archivos
Python coinciden con su commit. 313 pruebas final y 128 M3 aprobaron (441).
Notebook sin celdas de error. `setup_ok=true`, siete peticiones conservadas,
`completed_requires_review`, cero errores técnicos inesperados. La entrada
vacía fue rechazada deliberadamente; no es un fallo de ejecución del sistema.

Tesla T4, Python 3.13.16, Torch 2.14.1+cu130, Gradio 6.16.0, Hub 0.36.2,
Transformers 4.57.6. Los cinco modelos y el índice cargaron; tiempo de carga
observado 306,43 s. No comparar estas latencias con el experimento de eficiencia
ni extrapolar a ZeroGPU/Python3.12/Torch del alojamiento.

| Caso | Observación |
|---|---|
| QA de entidad | AEROCIVIL, respuesta correcta y fuente presente; explicación poco precisa sobre dónde aparece la entidad. |
| M1 | SUFICIENTE, clasificador real usado. Confianza 0,9595 no calibrada; un ejemplo no valida su exactitud. |
| Cálculo | 250000000 − 82000000 = 168000000 COP, herramienta exitosa y citas de los operandos. |
| Imagen de ficha | Error OCR: 250000000 leído como 2500000000. Discrepancia detectada y respuesta bloqueada. No es lectura correcta. |
| Informe inexistente | Abstención por fuente ausente. |
| Imagen blanca | Abstención por ilegibilidad; control de píxeles, no prueba de OCR exitosa. |
| Entrada vacía | Rechazo invalid_input esperado. |

La imagen original se inspeccionó visualmente: el importe impreso es 250000000,
sin cero adicional. El fallo no se debe a discrepancia real de documentos. El
control impidió afirmarlo, pero bloqueó incluso la pregunta de entidad que sí
era visible: falsa abstención desde el punto de vista de utilidad de esa entrada.
No cambiar silenciosamente el control para dejar pasar esta discrepancia.

Los siete eventos cumplen el esquema sin pregunta/imagen/OCR/respuesta. Los
registros con contenido guardados en este ZIP son evidencia local de prueba,
no telemetría de producción ni llamadas públicas W&B. `success=true` describe
éxito técnico, no acierto. `semantic_quality_approved=false` se conserva.

La corrida no modifica el scorecard de 22 casos ni sus seis fallos FP16. La
replicación visual 18 está fijada después de inspeccionar este fallo y será
diagnóstica/post-hoc, no validación ciega. Main y el Space no se actualizan aquí.
