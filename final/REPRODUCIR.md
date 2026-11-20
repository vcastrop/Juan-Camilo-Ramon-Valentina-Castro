# Reproducción de la entrega

## Usar el sistema, sin instalar nada

1. Abrir https://huggingface.co/spaces/Juanoff/contractrisk-colombia .
2. Seleccionar consulta o M1, introducir texto o una ficha pública y aceptar el aviso.
3. Consultar y revisar resultado, explicación y fuentes. No introducir datos personales.
4. Consultar salud sin GPU con el botón o `/healthz` y `/readyz` en la URL directa
   de la app (`juanoff-contractrisk-colombia.hf.space`). Ready503 significa no listo.

La demo no requiere una clave pagada del visitante. ZeroGPU aplica cuota y cola.
M1 señala suficiencia descriptiva; no detecta fraude. Las capturas son sintéticas.

## Recuperar tablas ya medidas, sin GPU ni API

Requiere Python3.12 o3.13 y Git con historial completo. Ejecutar desde la raíz:

```powershell
git clone --branch Entrega/contractrisk-final https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro.git
cd Juan-Camilo-Ramon-Valentina-Castro
python -m venv .venv
.venv\Scripts\python -m pip install -r final/requirements-api-judge.txt
.venv\Scripts\python final/prepare_test_history.py
.venv\Scripts\python -m final.build_delivery_tables --output reproduccion_final
.venv\Scripts\python -m unittest discover -s final/tests -q
.venv\Scripts\python -m unittest discover -s m3/tests -q
```

Linux/Colab: cambiar `.venv\Scripts\python` por `.venv/bin/python`, o usar el
Python del notebook. `prepare_test_history` no cambia el checkout; necesita los
commits auditados. No usar clon shallow. El nombre del script requirements es
histórico: instalarlo no hace llamadas al juez.

Se obtienen `reproduccion_final/tables.json` y `tables.md`, recalculados desde
predicciones, notas crudas, revisión humana y logs conservados. El comando
rechaza sobrescribir una carpeta previa. No regenera respuestas ni cobra API.
Las pruebas que simulan503 no son solicitudes reales al proveedor.

## Reejecutar modelos (opcional y separado del recálculo)

- Comparación histórica: `ContractRisk_Final_Comparacion_02_Colab.ipynb`, TeslaT4.
- Perfil visual final: `ContractRisk_Final_Integracion_20_Colab.ipynb`, TeslaT4,
  Tesseract5.3.4 spa+eng. Consultar sus originales y commits fijados en evidencias.
- El benchmark FP16/NF4 usa un mismo conjunto22 y sesión; mantener hashes,
  parámetros, semilla42 y versiones. En el perfil OCR otra sesión produce tiempos
  descriptivos; no mezclarlo con la comparación controlada de eficiencia.
- Los notebooks históricos pueden clonar la rama vigente. Para reproducir la
  corrida exacta usar su commit registrado; no asumir equivalencia con HEAD.
- Una reejecución no garantiza valores idénticos en otra GPU/entorno.

El juez externo solo se necesita para obtener notas nuevas. Recalcular las tablas
y usar la demo no lo requiere. Si falta GEMINI_API_KEY, los evaluadores detienen
esa etapa y conservan parciales; no inventan notas. No ejecutar notebooks de
reanudación21 ni reiniciar el presupuesto Drive: el cierre ya está conservado.

## Reconstruir el paquete público

Commit de inferencia `5b42adc35d6e3225c93dfbda13ae2e1730bad1c8`. Obtener la licencia
Qwen Research fijada en `final.build_space_candidate.LICENSE_URL`, verificar
`LICENSE_SHA`, y ejecutar el constructor `final.build_space_ocr` desde ese commit
con `--output` nuevo y `--license-file`. Ver DESPLIEGUE_OCR_22.md. Subir juntos
los archivos generados, no las referencias ni notas del juez.

W&B usa WANDB_API_KEY como secreto y entity/project/baseURL documentados en el
Space. Sin clave, inferencia funciona pero telemetría se declara deshabilitada.
Las métricas guardadas de la run pública son consultables; su estado Crashed
es un límite de continuidad no resuelto, no una aprobación de monitoreo estable.
