# ContractRisk: proyecto integrador

[Reporte](reporte.md) · [Reproducción sin pago](REPRODUCIR.md) ·
[Demo](https://huggingface.co/spaces/Juanoff/contractrisk-colombia) ·
[Run W&B](https://forge.coreweave.com/wandb/jcramonp-eanit/contractrisk-final/runs/f7ljlxip)

Perfil OCR FP16:18/22 dominio, juez4,455/5. NF4 rechazado por pérdida de calidad.
Servicio con cuatro modelos y TesseractCPU; siete rutas funcionales verificadas,
salud/accesos sin sesión comprobados. La run W&B conserva métricas pero figura
Crashed: continuidad no resuelta. No hay certificación para decisiones legales.

## Material vigente

- [Tablas de seis perfiles](evidence/delivery_tables/tables.md) y [generador offline](build_delivery_tables.py).
- [Conjunto común](eval/common_v1/), [política de eficiencia](efficiency_policy.json),
  [rúbrica](RUBRICA_JUEZ_FINAL.md) y [scorecard OCR](evidence/evaluation21_completed/scorecard.json).
- [Evidencia visual/semántica](evidence/evaluation21_completed/ANALISIS.md),
  [smoke público](evidence/space_ocr23_cpu/SMOKE_RECIBIDO.md),
  [eventos auditados](evidence/space_ocr23_cpu/events_audit.json) y
  [acceso público](evidence/space_ocr23_cpu/ACCESO_PUBLICO.md).
- [Código/guía de despliegue](DESPLIEGUE_OCR_22.md), [constructor](build_space_ocr.py).
- [Diagrama](ARQUITECTURA.mmd), [presentación y demo](presentacion/GUIA_DEMO.md),
  [contribuciones/IA](CONTRIBUCIONES.md), [checklist](CHECKLIST.md).

No repetir notebooks pagados o de reanudación. El recálculo no requiere claves.
Originales y fallos quedan en evidence. [README histórico](HISTORIAL_README_DESARROLLO.md)
conserva estados antiguos, no instrucciones vigentes de ejecución/presupuesto.
