# Verificación de despliegue 17 — instalación compatible y parada segura

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
