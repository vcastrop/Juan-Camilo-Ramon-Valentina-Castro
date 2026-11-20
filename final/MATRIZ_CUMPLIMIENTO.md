# Cierre de requisitos de la entrega

Estado documental del 19/11/2026. No sustituye revisión del equipo, calificación ni entrega en Interactiva.

| Requisito | Evidencia | Estado / límite |
|---|---|---|
| Problema, usuario, decisión y éxito | [Reporte](reporte.md) | Documentado; utilidad aproximada por dominio, no estudio con usuarios |
| Integración y procedencia M1–M5 | [Diagrama](ARQUITECTURA.mmd), reporte | Cuatro modelos + OCR; M2 aporta evaluación, no se compara MacroF1 con QA |
| Evolución bajo evaluación común | [Tablas](evidence/delivery_tables/tables.md) | Seis perfiles; 22 entradas; límites y adaptación del control explícitos |
| Técnica eficiente y antes/después | Reporte, tablas | FP16/NF4 en misma T4; NF4 rechazado por calidad y regresiones |
| Ablación y cinco errores | Reporte | Cuatro fallos actuales y uno histórico resuelto, identificados por separado |
| Juez y revisión humana | Evidencias14/21 enlazadas en reporte | Notas crudas conservadas; juez no ve píxeles ni reemplaza revisión humana |
| Servicio público completo reducido | [Space](https://huggingface.co/spaces/Juanoff/contractrisk-colombia) | Siete consultas válidas; cuatro modelos + Tesseract, no VLM ni NF4 |
| Salud y registros sin datos de entrada | [Evidencias23](evidence/space_ocr23_cpu/SMOKE_RECIBIDO.md) | Salud y diez eventos auditados; tres rechazos de entrada no son fallos de modelos |
| Observabilidad pública | [Run](https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/f7ljlxip) | Métricas y acceso público recibidos; Crashed sin causa resuelta: no estabilidad continua |
| Reproducción sin clave pagada obligatoria | [Instrucciones](REPRODUCIR.md) | Recálculo offline; reejecutar modelos es etapa separada con GPU |
| Ética, licencias, privacidad e IA | Reporte, NOTICE y licencia en payload | Datos públicos/sintéticos; caché temporal y límites declarados |
| Contribuciones | [Equipo](CONTRIBUCIONES.md) | Roles confirmados; no se reasignan revisiones firmadas |
| Diapositivas y demo de hasta diez minutos | [PowerPoint](presentacion/ContractRisk_Final.pptx), [guion](presentacion/GUIA_DEMO.md) | Preparados; falta revisión y ensayo de ambos |
| Portada e índice | [README raíz](../README.md) | Demo, W&B, ejecución, módulos y reporte enlazados |
| Revisión final humana | Reporte, diagrama y diapositivas | Pendiente del equipo |
| Sustentación | Fecha/hora/modalidad y preguntas individuales | Pendiente de confirmar con el curso; coordinar antes del 23/11 |
| Video de respaldo / CI opcional | Guion | Recomendado / opcional; no se declara realizado |
| Publicación y entrega formal | Rama Entrega/contractrisk-final | No equivale a merge ni entrega; conservar comprobante real de Interactiva |

La versión pública y los resultados no certifican fraude, autenticidad ni decisiones contractuales reales.
