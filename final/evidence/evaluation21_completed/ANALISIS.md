# Cierre OCR20: evaluación21 recibida y auditada

- ZIP original SHA-256: `f47d0584e6048c6117cc2b60b0c39b093edbfa9ec0aac1a0ff4d53e9fbb94fbd`.
- Notebook original SHA-256: `3856f0572831700672c121ff388e691d7eab519295220fe7b07efbbc189ac2eb`.
- Checkout `576a51112cd1f774785a68821cae98285bdfbe86`. Celdas coinciden con
  el código publicado, todas ejecutadas y sin excepciones de celda.
- 22 notas válidas: catorce transferidas por igualdad exacta y ocho nuevas,
  ocho despachos API sin reintentos. No se regeneran respuestas ni ajustan notas.
- Media del juez 98/22 = **4,4545/5**; ocho notas nuevas de 5. Los motivos
  identifican modalidad/valor y cita visual. El juez recibe extracción, no píxeles:
  la revisión humana firmada contrasta los datos con la imagen.

## Cruce sin cambiar reglas

Se ejecuta `domain_scorecard14.join_row` con las mismas reglas: estructura,
abstención, trazabilidad, cinco criterios semánticos, ausencia de crítico y nota
LLM ≥4. Doce revisiones textuales se transfieren; diez visuales son revisión nueva.

| Dimensión | OCR20 |
|---|---:|
| Cobertura literal media (diagnóstico, no exactitud) | 0,7121 |
| Juez crudo 1–5 | 4,4545 |
| Dominio /22 | 18/22 (81,82 %) |
| Dominio textual /12 | 8/12 |
| Dominio visual /10 | 10/10 |

Frente a 16/22 del FP16 visual histórico, mejora dos casos, no dos contratos
independientes. Las preguntas y referencias ya estaban inspeccionadas; no es gold
ciego ni prueba de generalización. Cuatro fallos textuales siguen: m3_003,
m3_005 y m3_006 incompletos/imprecisos, y m3_009 con cronología invertida en la
explicación. En m3_006 el juez da 4, pero el humano rechaza completitud; dominio
lo rechaza sin bajar artificialmente la nota. No se reparan esas respuestas.

Las dos abstenciones visuales son adecuadas según revisión humana, contraste y
rotación conservan respuesta. En vis_07 el OCR elimina la instrucción adversarial
antes del generador: el resultado es correcto, pero no prueba inmunidad de éste.
El OCR acotado omite encabezado/entidad y no demuestra lectura universal. Dos
segmentaciones del mismo motor no son jueces independientes ni confianza calibrada.

## Presupuesto e integridad

Se conservaron idénticos los 167 asientos previos. Hay ocho nuevos, 175 totales,
liquidados contra uso informado. Incremento estimado USD0,1225200; acumulado
estimado/reservado **USD5,9179725**, dentro de USD7 TOTALES. No es factura.
El cierre no autoriza más gasto ni libera reservas antiguas.

El `summary.json` bruto decía revisión humana pendiente porque Colab no recibe
firmas. Se conserva intacto. `scorecard.json` es un derivado posterior que cruza
la revisión firmada ya recibida. Reproducción offline, sin API:

```powershell
python -m final.evaluation21_audit --output cierre21_recalculado.json
```

Este cierre no verifica el Space, W&B público ni una nueva comparación de
eficiencia. NF4 conserva su rechazo histórico. Siguiente hito: desplegar el
perfil OCR20 (cuatro modelos neuronales y Tesseract) y probarlo públicamente.

Verificación local: tres pruebas nuevas de recepción/recálculo y veinte pruebas
de evaluación21, recepción humana y reglas de dominio pasaron, sin llamadas API.
