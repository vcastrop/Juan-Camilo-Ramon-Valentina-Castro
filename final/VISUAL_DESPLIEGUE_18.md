# Diagnóstico visual acotado 18

La [corrida 17 completada](evidence/deployment17_completed/ANALISIS.md) prueba
inferencia técnica real de M1/RAG/herramienta/visión, pero la captura produjo un
cero extra. Este diagnóstico conserva modelos, revisiones, prompts, extracción,
límites y guardas. **No es una corrección del modelo ni una nueva evaluación ciega.**

## Ocho entradas congeladas antes de GPU

`evidence/visual18_protocol/protocol.json` contiene expectativas solo diagnósticas,
SHA de cada PNG y huellas de todos los archivos de inferencia del payload 17.
El ejecutor verifica esas huellas. Modelos reciben únicamente pregunta, imagen
y corpus ordinario; expectativas se usan después para analizar resultados.

Preparación local comprobada: ocho pruebas nuevas pasan, incluidos ejecución
simulada de ocho entradas, ausencia de expectativas en la llamada de inferencia,
rechazo de PNG alterado y conservación de parciales sin reintentar. La suite
final previa más seis pruebas iniciales pasó (319) y M3 pasó (128); las dos
pruebas restantes del ejecutor se comprobaron después dentro del bloque de ocho.
No se han ejecutado estos ocho casos con modelos reales todavía.

1. Captura original exacta: una replicación explícita de OCR, no reemplaza el fallo
   17. La pregunta ahora solicita modalidad/valor; no es repetición idéntica de
   la respuesta a la pregunta de entidad. El prompt de lectura visual no cambia.
2. Primera ficha, diseño compacto y cifra sin separadores.
3. Misma ficha compacta, cifra con separadores de miles.
4. Segunda ficha compacta, cifra sin separadores.
5. Misma segunda ficha, cifra con separadores.
6. Valor alterado deliberadamente respecto al snapshot.
7. Ficha sin valor: se solicita valor y modalidad.
8. Imagen blanca.

Las cinco legibles y tres controles se informan separadamente. Una abstención
ante OCR errado no cuenta como lectura correcta. Se conservan todas las salidas
en una sola pasada; sin nuevas muestras, cambios de prompt ni repeticiones para
buscar aciertos. Es una muestra pequeña seleccionada post-hoc, no representativa
del dominio; no permite concluir mejora general ni causalidad por el formato.

Los chequeos automáticos de texto son literales, no comprensión de negaciones o
validación humana. `deployment_quality_approved` permanece falso: se revisarán
imágenes, transcripciones, citas y respuestas completas. Un éxito en un formato
no borra el fallo original ni autoriza cambiar cifras por consulta al gold.

## Ejecución

Abrir `ContractRisk_Final_Visual_18_Colab.ipynb`, GPU T4, celdas en orden.
No se necesitan claves ni pagos. La instalación reutiliza paquetes/pesos
cacheados si están disponibles. No repetir 17 ni el benchmark final.
Enviar ZIP y notebook descargado con salidas. Si falla, descargar parcial desde
la última celda; no corregir salidas manualmente ni repetir por cuenta propia.

## Después de esta única tanda

Documentar qué lecturas funcionaron, falsos bloqueos y cualquier respuesta
potencialmente insegura. Decidir alcance de la función visual del prototipo con
esa evidencia, sin iniciar búsqueda abierta de modelos o prompts. A continuación
verificar el candidato experimental en ZeroGPU, salud, consultas reales y W&B
público/accesible. Colab no demuestra esos hitos. No subir archivos al Space aún.
