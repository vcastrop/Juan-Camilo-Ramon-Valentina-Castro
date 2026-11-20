# Visual 18: técnica completada, utilidad visual rechazada

Se preservan los originales:

- ZIP SHA256 `d7d87a2f146ebacfad458214cb9a45c7f45fe999acf9628ba536398d0285df34`.
- Notebook SHA256 `c1cb6a51c18b0195a33315c72f7416651dde32264cbec3df31224e9c9348b459`.
- Código `ff951c72e08925fd3f47312e3a07b4c0e271017e`.
- Protocolo SHA256 `cc1f3a9ac6b466d49a479a98029a0c6e2d73bfe570196071f641e25548112b3d`.

Entradas y hashes coinciden exactamente con el protocolo congelado. Diagnósticos
recalculados coinciden. Notebook sin errores de celda; 321 pruebas final y 128
M3 (449) aprobadas. T4, Torch 2.14.1+cu130; sin API pagada. No equivale a calidad.

Ocho casos completados. **0/5 legibles útiles**, todos terminaron en abstención.
La imagen original repitió 250000000 → 2500000000, bloqueada por contradicción.
Las cuatro compactas solo produjeron el encabezado; ningún campo contractual.
No hay evidencia para atribuir causalidad al encabezado o al formato en general.

En valor alterado y valor ausente también solo leyó el encabezado: el bloqueo
fue `visual_schema`, no los controles esperados `visual_source_conflict` y
`missing_visual_fields`. Por eso **3/3 abstenciones en controles no significan
3/3 detecciones correctas**. Solo el blanco activó la ruta esperada, por guardia
de píxeles, sin inferencia VLM. No hubo respuestas potencialmente inseguras
según el chequeo de esta muestra, pero la utilidad visual quedó rechazada.

No cambiar métricas históricas ni afirmar que FP16 ahora obtiene 0/22: este es
un diagnóstico post-hoc de otras entradas. `deployment_quality_approved=false`
se conserva; no publicar como lector visual validado. Main y Space sin cambios.

La siguiente propuesta es un candidato OCR distinto, con versión y protocolo
propios. No supone que Tesseract haya funcionado ni autoriza sustituir la
comparación final por resultados del nuevo lector. Primero comprobar OCR en CPU;
solo si aporta lectura útil, integrar y verificar controles/sistema afectados.
