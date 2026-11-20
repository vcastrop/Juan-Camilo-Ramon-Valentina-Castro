# Verificación de despliegue 17 — instalación compatible y parada segura

**Estado más reciente:** [corrida 17 completada](evidence/deployment17_completed/ANALISIS.md),
sin errores de celda. La técnica funciona en T4; OCR añadió un cero, detectado por
el control. No repetir 17: continuar con [diagnóstico visual 18](VISUAL_DESPLIEGUE_18.md).
Las instrucciones de reparación siguientes son históricas, ya no pendientes.

**Actualización de recepción:** la instalación y T4 ya pasaron en la corrida
17 recibida. Las pruebas se detuvieron porque el clon superficial omitía
historial necesario. [Auditoría y originales](evidence/deployment17_failed/ANALISIS.md).
Se corrigió la clonación y se añadió `prepare_test_history.py`; no se cambia
el código de inferencia ni se saltan pruebas.

La [prueba 16](evidence/deployment16_failed/ANALISIS.md) no llegó a inferencia:
Gradio 6.32.0 y Hub 0.36.2 eran incompatibles. No hay nuevas respuestas que
evaluar ni cambios en las métricas anteriores. No cambiar la API del juez.

El candidato usa ahora Gradio **6.16.0**, con Hub **0.36.2** y el resto de
dependencias/modelos/prompt/precisión conservados. La versión de interfaz se
refleja también en el README del Space. No subir nada aún al Space actual.

## Pasos

1. Abrir `ContractRisk_Final_Despliegue_17_Colab.ipynb`, no el notebook 16.
2. Crear una sesión nueva, **GPU T4**.
3. Ejecutar celdas en orden. No hacen falta secretos ni pagos.
4. Si falla instalación o comprobación, no ejecutar inferencia: pasar a la última
   celda y descargar el diagnóstico. No instalar `chromadb` por separado para
   ocultar el conflicto original. La celda de inferencia tiene bloqueo adicional.
5. Enviar ZIP y notebook con salidas: **Archivo → Descargar → Descargar .ipynb**.

El control de entorno verifica versiones y requisitos cruzados, no la calidad
de los modelos. Su informe muestra paquetes ausentes sin lanzar un segundo
error por falta de metadata. La envoltura de ejecución conserva metadata incluso
si falla antes de cargar modelos. El ZIP incluye diagnóstico aunque no haya
inferencias. Resultados parciales no equivalen a aprobación.

Después de revisar T4, queda probar el ciclo de vida real de ZeroGPU y las
peticiones/telemetría desde URL pública. La instalación local de la interfaz no
demuestra esas etapas. No hay cambios a main ni a los cuatro archivos del
Space de infraestructura en esta corrección.

## Reutilizar la sesión 17 que ya instaló las dependencias

Antes de repetir la celda de preparación, completar el historial en una celda:

```python
antes = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
if subprocess.check_output(['git', 'rev-parse', '--is-shallow-repository'], cwd=ROOT, text=True).strip() == 'true':
    run_visible(['git', 'fetch', '--unshallow', 'origin', 'Entrega/contractrisk-final'], 'deployment17_history.log')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == antes
print('Historial completado sin cambiar el código.')
```

Repetir después la celda de preparación; no la primera de clonación. Si termina
sin error y habilita `SETUP_OK`, ejecutar inferencia y descarga. Conservar ZIP
y notebook con salidas, incluida esta celda de reparación. No requiere reiniciar,
cambiar bibliotecas, claves ni facturación. Si la sesión ya terminó, usar el
notebook 17 actualizado desde GitHub en una sesión nueva con T4.
