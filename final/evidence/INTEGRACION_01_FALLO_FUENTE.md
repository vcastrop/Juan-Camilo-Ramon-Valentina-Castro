# Integración 01 — fallo de fuente en Colab

16/11/2026. Capturas del usuario: la ejecución llegó a autenticarse en W&B pero falló al crear fixtures, antes del mensaje de carga del clasificador. Error causal: ausencia de DejaVu Sans en las rutas de sistema supuestas. La prueba local anterior había encontrado Arial en Windows y no demostró disponibilidad de fuentes en Colab.

Corrección: dependencia explícita `matplotlib==3.10.6` y uso directo de su DejaVuSans.ttf empaquetada, sin depender de fuentes instaladas en el sistema. El hash de la fuente se guarda con la ficha de prueba. Se añade prueba de resolución con sistema simulado sin fuentes y error explícito si falta la dependencia.

El aviso de TensorFlow sobre ausencia de CUDA no es el error que termina el traceback. El runner ya había comprobado PyTorch CUDA. Se deshabilita la importación opcional TensorFlow para estos adaptadores PyTorch; no cambia el hardware ni sustituye mediciones.

No borrar la carpeta ni la run fallidas. Ejecutar la corrección con una carpeta de salida nueva. La run W&B recibe estado de ejecución y calidad no aprobada antes de finish; un cierre limpio no significa inferencia correcta.
