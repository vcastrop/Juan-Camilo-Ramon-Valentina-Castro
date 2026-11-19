---
title: ContractRisk Colombia
emoji: 📋
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.32.0
python_version: 3.12
app_file: app.py
pinned: false
---

# ContractRisk Colombia — candidato académico

**Built with Qwen. Solo investigación y evaluación no comercial.**
Consultas sobre 24 fichas públicas colombianas, cálculos acotados y lectura de
capturas. El modo M1 clasifica suficiencia descriptiva: **no detecta fraude**.
Las fuentes y toda decisión deben revisarse por una persona. El FP16 evaluado
cumplió dominio en 16/22 entradas; mantiene seis fallos conocidos. No es un
servicio certificado para decisiones legales o contractuales.

## Archivos y arranque

El paquete generado contiene `app.py`, `requirements.txt`, este `README.md` y
`runtime_payload.zip`. No subir la plantilla `app.py` directamente: requiere el
hash y commit que inserta `final/build_space_candidate.py`.
No sustituir todavía el Space de infraestructura sin la prueba de modelos reales.

El ZIP incluye código de inferencia, corpus, adaptador M1, manifiesto y avisos de
licencia. No contiene gold, resultados, juez ni claves. Las revisiones de los
cinco modelos están fijadas en `final/config.py`. Pesos base se descargan al
iniciar, no dentro de la petición GPU. Se conserva generador FP16; no hay
fallback NF4/CPU ni respuestas cacheadas. Arranque frío puede tardar varios minutos.

Importar `spaces` antes de CUDA; inicialización en CUDA emulada durante el
arranque e inferencia dentro de `@spaces.GPU`. `spaces` y `torch` los gestiona el
constructor de ZeroGPU: no fijar otra versión incompatible en requirements.
La prueba Colab no sustituye verificar el ciclo de vida real de ZeroGPU.

## Salud y registros

- `/healthz`: proceso vivo, sin pregunta real ni inferencia GPU.
- `/readyz`: HTTP 200 solo con modelos e índice comprobados; 503 si no están listos.
- `real_request_verified` es distinto de readiness: solo cambia tras una petición
  completada en esta instancia; no representa corrección semántica.
- JSON técnico y W&B: hora, duración de procesamiento, versión, éxito técnico,
  modo, componentes, router, herramienta exitosa y abstención. No pregunta,
  descripción, OCR, respuesta, ID contractual ni archivo de imagen.
- La duración excluye cola/asignación de ZeroGPU y envío a W&B. No compararla
  con la medición controlada de eficiencia en T4.

Opcional: secreto `WANDB_API_KEY`, variables `WANDB_ENTITY=jcramonp-eanit` y
`WANDB_PROJECT=contractrisk-final`. Sin clave la inferencia sigue disponible y
se declara telemetría deshabilitada. No requiere `GEMINI_API_KEY` ni otra API
pagada. La versión procede del manifiesto, no de `CONTRACTRISK_VERSION`.
`queued_check_dashboard` no garantiza sincronización o acceso del evaluador.

## Privacidad, límites y licencias

Solo fichas públicas sin datos personales. No cargar documentos privados.
El framework puede mantener imágenes temporalmente en caché; limpieza periódica
configurada cada hora para archivos con más de una hora (no borrado inmediato
garantizado). Límite 10 MB y 12 millones de píxeles. Cola acotada, concurrencia
uno; la disponibilidad/cuota GPU depende del proveedor. El consentimiento no
elimina estos límites. Los proveedores de alojamiento mantienen sus propias
políticas de acceso y retención.

Qwen2.5-3B-Instruct usa **Qwen Research License**, no Apache 2.0. Copia en
`runtime_payload.zip/licenses/QWEN_RESEARCH_LICENSE.txt`; aviso en `NOTICE.txt`.
[Licencia oficial fijada](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/aa8e72537993ba99e69dfaafa59ed015b17504d1/LICENSE).
Los otros modelos declaran Apache 2.0 en sus tarjetas; no se redistribuyen sus
pesos base. Procedencia/revisiones en el manifiesto. No se cambia su licencia
por la del código de esta aplicación.

Repositorio y evidencia: [ContractRisk](https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro/tree/Entrega/contractrisk-final/final).
