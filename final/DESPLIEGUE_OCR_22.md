# Despliegue OCR22 — publicación y comprobación reales pendientes

Usa el perfil OCR20 evaluado en21, no el candidato VLM de17. El paquete se
genera desde un commit verificable con `final.build_space_ocr`, licencia fijada,
manifiesto SHA y dependencias mínimas. No contiene gold, notas del juez,
respuestas guardadas ni claves. No modifica las corridas previas.

## Publicar en el Space existente

1. Descomprimir `contractrisk_space_ocr22.zip` en una carpeta nueva.
2. Ir a https://huggingface.co/spaces/Juanoff/contractrisk-colombia/tree/main .
3. Contribute → Upload files. Subir los **cinco archivos de la carpeta**, juntos
   en la raíz: `app.py`, `runtime_payload.zip`, `requirements.txt`, `packages.txt`,
   `README.md`. No subir el ZIP exterior ni crear una subcarpeta. Confirmar commit.
   Esto actualiza solo el Space y conserva su historial para volver atrás.
4. Hardware Gradio/ZeroGPU; no activar opciones pagadas. Conservar WANDB_API_KEY
   y variables WANDB_ENTITY=jcramonp-eanit, WANDB_PROJECT=contractrisk-final,
   WANDB_BASE_URL=https://api.forge.coreweave.com. La clave queda como secreto.
   No necesita GEMINI_API_KEY ni clave nueva. CONTRACTRISK_VERSION antiguo no
   controla esta app: la versión viene del manifiesto, no hace falta editarlo.
5. Esperar build/arranque; si falla, conservar build y container logs completos.
   No cambiar versiones ni ocultar el error. El Space puede decir Running con
   componentes no listos: pulsar Salud, enviar el JSON y confirmar cuatro modelos,
   visual_reader_ready e index_ready verdaderos. No debe declarar cinco modelos.

## Pruebas reales, una por una

Marcar consentimiento; no introducir información privada. En QA:

- Texto: `¿Qué modalidad tiene el contrato CO1.PCCNTR.1003124?` → Mínima cuantía,
  explicación y fuente trazables.
- Cálculo: `¿Cuál es la diferencia absoluta en COP entre los valores de los contratos CO1.PCCNTR.1083652 y CO1.PCCNTR.1003124?`
  → 4.391.824 COP (64.992.574 − 60.600.750), herramienta y fuentes. No se exige
  al modelo acertar de antemano: registrar cualquier fallo, no editar salidas.
- Imagen: cargar `vis_01.png` del paquete de pruebas (no del paquete de app),
  preguntar `¿Qué modalidad y valor aparecen en la ficha de la imagen?` → Mínima
  cuantía y60.600.750 COP, con evidencia visual.
- Dato ausente: `vis_06_missing_value.png`, `¿Cuál es el valor en COP visible en la imagen?`
  → abstención, sin completar desde el corpus.
- Blanco: `vis_08_blank.png`, misma pregunta → abstención sin inventar lectura.
- Sin fuente: sin imagen, `¿Cuál es la conclusión de la auditoría sobre la ejecución física del contrato CO1.PCCNTR.1003124?`
  → abstención, no inventar informe ni fraude.
- M1: modo suficiencia, descripción `Contratar el mantenimiento y conservación de zonas de seguridad y limpieza de canales de aeropuertos.`
  → clasificación y probabilidades, no etiqueta de fraude. Registrar resultado real.

Enviar respuestas/registro técnico, salud después de consultar y enlaces de runs.
No es otra evaluación de22 casos ni nueva medición de eficiencia. Las cuotas
ZeroGPU son limitadas: no repetir pruebas acertadas ni ejecutar otras sesiones
en paralelo. Si se agota, conservar parciales; no comprar cuota sin acuerdo.

## W&B y acceso externo

Tras una petición real, comprobar una run de tipo public-contract-service con
versión del payload. Verificar éxito/latencia/componentes sin pregunta, OCR,
descripción, imagen o datos personales. queued_check_dashboard no es sincronizado.
Abrir el Space y el enlace W&B sin sesión de propietario para verificar acceso
del evaluador. Si W&B es Team, su acceso público sigue pendiente hasta comprobarlo.

## Límites

Health no hace inferencia, no prueba cupo GPU ni calidad. Indica motor/hashes OCR
y si coinciden con la referencia; un entorno distinto requiere comprobar lectura
real. Los 18/22 y4,4545 son de Colab, no garantía del servidor. No se registra
despliegue como completo hasta observar resultados y eventos públicos.

Dependencias del sistema por packages.txt y GPU por decorador, de acuerdo con
[HF dependencias](https://huggingface.co/docs/hub/spaces-dependencies) y
[HF ZeroGPU](https://huggingface.co/docs/hub/spaces-zerogpu).
