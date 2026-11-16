# ContractRisk — entrega integradora en desarrollo

Estado: preparación de infraestructura, no sistema final funcional. [Checklist](CHECKLIST.md).

Objetivo: integrar la señal de suficiencia descriptiva M1, consultas con fuentes/herramienta M3 y lectura de capturas contractuales, medir eficiencia y desplegar una aplicación observada.

Space objetivo: https://huggingface.co/spaces/Juanoff/contractrisk-colombia

Equipo W&B: `jcramonp-eanit`; proyecto propuesto: `contractrisk-final`. No se ha verificado autenticación ni registro remoto.

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
