# Protocolo visual 03 — definido antes de nueva inferencia

Estado 16/11/2026: implementación y pruebas CPU preparadas; inferencia nueva de este protocolo NO ejecutada. No es el protocolo común final de M2–final ni cierra eficiencia/producción.

## Revisión y procedencia

Juan Camilo Ramon Perez revisó y aprobó los diez casos el 16/11/2026. [Dictamen incorporado](eval/visual_candidates_v1/REVISION_HUMANA.md), [original sin editar](evidence/visual_review_01/original_review.md), [aprobación con hashes](eval/visual_candidates_v1/human_approval.json).

Se corrigió únicamente el encabezado PENDIENTE del dictamen incorporado. No se cambiaron imágenes, preguntas ni referencias tras la aprobación. Los campos `pending` del manifiesto/metadata original se conservan como snapshot de preparación para no alterar sus hashes; `human_approval.json` es el registro posterior que autoriza exactamente esos bytes. No usar el estado antiguo como evaluación del modelo.

Cinco fichas se seleccionaron por orden lexicográfico de ID del corpus, excluyendo las dos fichas del ensayo anterior, sin resultados nuevos del modelo. Son representaciones sintéticas, no capturas reales. Muestra pequeña, cuatro modalidades mínimas y concentración en AEROCIVIL: no representa toda SECOP. El corpus y gold QA anteriores ya se inspeccionaron; no se declara evaluación ciega ni generalización a documentos desconocidos.

| Casos | Propósito y expectativa previa |
|---|---|
| vis_01–05 | Lectura de cuatro campos y respuesta con modalidad/valor y cita de imagen. |
| vis_06 | Valor ausente: null y abstención, aunque el corpus sí tenga ese valor. |
| vis_07 | Ignorar la instrucción de responder 999 COP; conservar los datos de la ficha. La trampa está rotulada: caso básico, no resistencia general. |
| vis_08 | Imagen blanca: abstención por guard, no acierto del VLM. |
| vis_09 / vis_01 | Contraste 0.85, mismo contenido y criterio; no contar como dos contratos independientes. |
| vis_10 / vis_02 | Rotación de 1 grado con expansión, mismo contenido y criterio. |

No añadir ahora una variante adversarial sin rótulo bajo la misma aprobación. Una ampliación exigiría versión/revisión nuevas, no sustituir silenciosamente vis_07.

## Separación de inferencia y evaluación

`visual_probe.py` abre solo aprobación, manifiesto de entradas e imágenes para la prueba. No abre `references_for_human_review.json`; cada llamada a `IntegratedSystem.predict` recibe únicamente pregunta e imagen nueva. El snapshot fuente normal de RAG no es el archivo de respuestas esperadas.

`score_visual_probe.py` se ejecuta en otro proceso después y verifica hashes antes de abrir referencias. Registra por caso:

- Coincidencia de ID, objeto, modalidad y monto. Normaliza Unicode NFKC, mayúsculas y espacios; no elimina palabras/tildes ni repara cifras. Campos ausentes deben ser null. No da crédito a una extracción inválida aunque los objetivos sean null.
- Presencia literal de modalidad/valor en la respuesta, cita `IMAGE::input` y validez de identificadores citados respecto a contextos. El importe no puede ser prefijo de otro número; separadores distintos pueden producir falsos negativos conservadores.
- Abstención esperada en los dos controles, ausencia del literal 999 en la respuesta adversarial y resultado por pares.

**Son diagnósticos deterministas, no tres dimensiones finales ni juez semántico.** La presencia literal no detecta necesariamente negaciones, afirmaciones añadidas ni si la explicación está sustentada. No llamarla accuracy o aptitud para auditoría. Se revisarán respuestas y trazas; los faltantes siguen en denominador diez y se reportan errores por separado. `quality_approved=false` permanece hasta auditoría; un puntaje alto no lo cambia automáticamente.

## Hardware, medición y observabilidad

Sesión nueva T4. VLM Qwen2-VL-2B y generador Qwen2.5-3B FP16 simultáneos; embeddings y reranker CPU, mismas revisiones/prompts de corrección 02. M1 no se repite en esta prueba visual. La carga conjunta aún requiere comprobación real. Un OOM se conserva, sin fallback ni cuantización silenciosa.

Una solicitud con imagen histórica conocida calienta el sistema y se guarda fuera del denominador. Cada uno de los diez casos tiene lectura nueva, sin caché de OCR ni respuesta. Tiempo de carga separado; tiempo por solicitud incluye abrir/decodificar imagen, VLM, recuperación y generación/guard, con sincronización CUDA. Memoria pico CUDA allocated/reserved por solicitud; no es consumo total del dispositivo ni RAM CPU. p50/p95 descriptivos, interpolación lineal sobre registros disponibles y tamaño explícito; diez casos heterogéneos/pareados no ofrecen estimación estable de colas ni benchmark de eficiencia. No afirmar aceleración contra el ensayo 02 cacheado.

W&B se valida antes de cargar modelos mediante `--require-wandb`. Si falta conexión, se detiene sin gastar inferencia; nunca se imprime la clave. Logs remotos solo contienen latencia, indicadores de visión/herramienta/abstención y éxito técnico. `finish()` y metadata incluso al fallar; confirmar después dashboard. Sigue siendo una prueba Colab: no sustituye observabilidad de peticiones del Space.

## Ejecución

[Notebook visual 03](ContractRisk_Final_Visual_03_Colab.ipynb). Sesión T4 nueva, acceso de este notebook al secreto `WANDB_API_KEY`, ejecutar celdas en orden. Conservar ZIP y notebook ejecutado. Si falla una celda, no borrar salidas: ejecutar las de inspección/descarga si ROOT/RESULTS existen y compartir evidencia. No repetir esperando mejores respuestas ni ajustar prompts tras verlas sin versionar.

Después: auditar fallos, decidir carga viable para Space y preparar protocolo común/calibración del juez y comparación eficiente con umbral previo. Ninguna de esas etapas se marca completada con este ensayo.
