# ContractRisk — entrega integradora en desarrollo

Estado: integración de desarrollo probada en T4; despliegue público todavía de infraestructura, no sistema final completo. [Checklist](CHECKLIST.md).

Última actualización: [API 07 auditada](evidence/api_07/ANALISIS.md) recibió 503 en la primera generación, sin ninguna nota. **Siguiente ejecución: [notebook API 08, recuperación única](ContractRisk_Final_Juez_08_API_Reintento_Colab.ipynb)** en runtime CPU, con [controles y límites](JUEZ_API_08_REINTENTO.md). No borrar marcas ni registro de Drive; se conserva la reserva original y no se habilita modo pagado. [Harness común candidato](HARNESS_COMUN.md) preparado sin comparación de modelos. No hay juez validado ni scorecard final.

Avance estimado al 18/11: **40–45 % de la entrega final**. [Desglose y ruta pendiente](PROGRESO_FINAL.md). El porcentaje reconoce preparación parcial; no sustituye resultados finales.

## Estado de la integración visual

[Visual 03 ejecutada y auditada](evidence/visual_03/ANALISIS.md): diez lecturas/rutas nuevas, carga conjunta en T4 y W&B con cierre confirmado por log. Un monto con cero adicional se propagó pese a contradecir el snapshot; se conserva el fallo, no se aprueba calidad global. [Control nuevo de consistencia 0.3](CONTROL_CONSISTENCIA.md) y reproducción CPU comprobados, sin cambiar respuestas históricas. Siguiente hito: protocolo común y evaluación/eficiencia, no repetir el ensayo para seleccionar mejores resultados.

[Notebook histórico visual 03](ContractRisk_Final_Visual_03_Colab.ipynb) y [protocolo original](VISUAL_03.md). El notebook clona la rama vigente: para reproducir exactamente la corrida original usar el commit `0935f20`, no suponer que una ejecución futura de la rama equivale a integración 0.2.

[Notebook de corrección 02](ContractRisk_Final_Correccion_02_Colab.ipynb) y [corrida ejecutada/auditada](evidence/correction_02/ANALISIS.md). Se corrigieron los problemas enfocados de lectura y elegibilidad de herramienta; todavía no es evaluación final. El [ensayo 01](evidence/integration_01/ANALISIS.md) se conserva con sus fallos originales. No subir estos archivos ni sus dependencias al Space inicial todavía.

La [revisión humana de diez casos visuales](eval/visual_candidates_v1/REVISION_HUMANA.md) se preservó. Los hashes están en `human_approval.json`; ya hay resultados auditados de visual 03. Las referencias están separadas del manifiesto de entradas y no deben enviarse al generador.

Objetivo: integrar la señal de suficiencia descriptiva M1, consultas con fuentes/herramienta M3 y lectura de capturas contractuales, medir eficiencia y desplegar una aplicación observada.

[Evaluación común y juez](JUEZ_Y_EVALUACION_FINAL.md): 22 entradas ensambladas con referencias separadas y veinte anclas aprobadas. Qwen y Mistral anteriores no pasaron; sus notas se conservan. [Mistral corregido](evidence/mistral_tokenfix/ANALISIS.md) dio 13/20 en rango; [Qwen3 con razonamiento](evidence/reasoning_04/ANALISIS.md), 19/20, pero ambos fallaron otros criterios obligatorios. El [protocolo de continuación vigente](JUEZ_CONTINUACION_06.md) reutiliza el prefijo del piloto 05 con evaluador corregido. No hay juez validado ni nuevo scorecard; confirmación separada y auditoría humana siguen pendientes.

[Reglas de eficiencia aprobadas](EFICIENCIA.md): máximo 5 puntos porcentuales de pérdida de cumplimiento, ningún fallo crítico nuevo ni regresión en controles, y al menos 20 % menos memoria pico CUDA asignada. Comprobación de aceptación preparada; comparación real y juez calibrado pendientes. No se desplegó cuantización ni se aceptó un resultado todavía.

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
