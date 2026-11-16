# ContractRisk — entrega integradora en desarrollo

Estado: integración de desarrollo probada en T4; despliegue público todavía de infraestructura, no sistema final completo. [Checklist](CHECKLIST.md).

## Próxima prueba: integración real en Colab

[Notebook de corrección 02](ContractRisk_Final_Correccion_02_Colab.ipynb) y [corrida ejecutada/auditada](evidence/correction_02/ANALISIS.md). Se corrigieron los problemas enfocados de lectura y elegibilidad de herramienta; todavía no es evaluación final. El [ensayo 01](evidence/integration_01/ANALISIS.md) se conserva con sus fallos originales. No subir estos archivos ni sus dependencias al Space inicial todavía.

Siguiente paso: [revisión humana de diez candidatos visuales](eval/visual_candidates_v1/REVISION_HUMANA.md). Abrir `index.html` de esa carpeta localmente para ver imágenes y referencias juntas. Todas las aprobaciones siguen pendientes; no se ejecutaron modelos sobre estos nuevos candidatos. Las referencias están separadas del manifiesto de entradas y no deben enviarse al generador.

Objetivo: integrar la señal de suficiencia descriptiva M1, consultas con fuentes/herramienta M3 y lectura de capturas contractuales, medir eficiencia y desplegar una aplicación observada.

Space objetivo: https://huggingface.co/spaces/Juanoff/contractrisk-colombia

Equipo W&B: `jcramonp-eanit`; proyecto: `contractrisk-final`. Las capturas del usuario confirman una run y asignación GPU real. La visualización de métricas, acceso del evaluador y observabilidad de consultas reales están pendientes. [Evidencia y límites](evidence/SPACE_SMOKE_CONFIRMADO.md).

## Prueba inicial de despliegue

Subir **el contenido de `final/space/` a la raíz del Space**: README.md, requirements.txt, app.py y telemetry.py. No subir credenciales, todo el proyecto ni el material del curso.

En Settings, crear Secret `WANDB_API_KEY` y Variables `WANDB_ENTITY` y `WANDB_PROJECT` según lo indicado en el README del paquete. Un secreto de Colab no se copia automáticamente.

Revisar App y Logs. `/healthz` debe responder 200 y `/readyz` debe responder 503 hasta que modelos e índice estén integrados. Pulsar una vez prueba técnica y comprobar el proyecto W&B; pulsar prueba GPU una vez para verificar asignación. No repetir mientras esté en cola.

`queued_check_dashboard` significa que el SDK aceptó el evento en su cola local, no que la entrega remota ya esté demostrada. Un fallo de W&B no bloquea el estado del proceso ni convierte la prueba en éxito.

## Verificación local sin modelos

```bash
python -m unittest discover -s final/tests -v
python -m unittest discover -s m3/tests -v
```

Los resultados M3 no se atribuyen a esta aplicación inicial. El protocolo final, la visión, la comparación eficiente y el reporte están pendientes. No se ha modificado main.
