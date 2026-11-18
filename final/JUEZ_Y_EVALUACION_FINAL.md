# Evaluación común y calibración del juez — preparación v1

Estado al 17/11/2026: veinte anclas aprobadas; **Qwen 7B ejecutado y rechazado** (15/20 en rango, cinco malos con nota alta y sesgo fuera de umbral). [Auditoría de corrida original](evidence/judge_calibration_01/ANALISIS.md). No hay juez validado ni comparación de eficiencia. [Segundo candidato Mistral y confirmación separada](JUEZ_02.md) preparados, no ejecutados. No se modifican main ni Space ni las notas históricas.

Actualización 18/11: [Mistral corregido ejecutado y auditado](evidence/mistral_tokenfix/ANALISIS.md): 38 entradas nativas, 13/20 en rango, siete malos con nota alta y diferencia de verbosidad máxima 3. La corrección de tokens no bastó para superar el filtro. [Nuevo protocolo por criterios y razonamiento](JUEZ_RAZONAMIENTO.md) preparado, aún sin inferencia. Se conservan todas las corridas y sus notas originales; no hay juez validado.

## Conjunto común ensamblado

[`eval/common_v1/inputs.json`](eval/common_v1/inputs.json) contiene 22 entradas: las doce preguntas QA de M3 y las diez imágenes ya revisadas. [`references.json`](eval/common_v1/references.json) conserva sus hechos/criterios por separado. En preguntas de cronología se transcriben los dos timestamps del esperado original como hechos a comprobar; no se inventan nuevas fechas.

No se cambiaron los montos para coincidir con la lectura errónea, ni se cambió vis_04 a «abstención correcta». Una abstención por conflicto protege, pero sigue sin responder el monto de esa imagen legible. El conjunto ya fue inspeccionado y parte se usó en desarrollo: no es gold ciego ni prueba de generalización. Variantes comparten contratos; 22 entradas no son 22 contratos independientes. Metadata guarda hashes canónicos resistentes a finales de línea, además de procedencia.

**Todavía no está congelado el protocolo completo.** Faltan el harness común, controles por caso y resultado de calibración. Esta preparación no autoriza a aplicar la política de eficiencia a métricas antiguas.

## Tres dimensiones que se conservarán separadas

- Automática: cobertura verificable de hechos requeridos y coincidencia de campos visuales, con reglas de número/negación y límites explícitos. No llamarla accuracy semántica si es coincidencia literal; no rescatar una abstención indebida porque su explicación menciona la cifra gold.
- Juez: puntuación **bruta** 1–5 de respuesta, explicación y respaldo en evidencia; no recibe expected, criterio gold, resultados automáticos, confianza ni comparación de etiquetas. Puntuación inválida permanece ausente; un único reintento solo de formato.
- Dominio: respuesta útil y respaldada o abstención justificada, citas válidas, controles de daño y criterio individual. Su definición y su uso del juez se congelarán antes de medir. No convertir automáticamente un acierto en nota 4 ni usar promedios para ocultar fallos críticos.

La tabla evolutiva deberá ejecutar las mismas entradas/harness: baseline QA sin RAG adaptado de M2, M3 textual, nueva base visual FP16 y final eficiente. M1/M2 clasificación original se informa aparte, porque su Macro F1 no es comparable a QA. Los sistemas sin visión recibirán la misma pregunta pero no una transcripción privilegiada: su limitación visual debe quedar explícita y los casos seguir en denominador. Esto todavía requiere implementación y comprobación de los adaptadores de comparación, no está marcado como corrida realizada.

## Juez candidato distinto del generador

[`judge_calibration_config.json`](judge_calibration_config.json): Qwen/Qwen2.5-7B-Instruct, revisión `a09a35458c702b33eeacc393d103063234e8bc28`, NF4, cómputo FP16 y doble cuantización, 320 tokens máximos, semilla 42. Modelo/revisión públicos verificados en la [API oficial de Hugging Face](https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct). Cuantización conforme a [Transformers](https://huggingface.co/docs/transformers/v4.57.0/quantization/bitsandbytes), dependencia `bitsandbytes==0.50.2` verificada en [PyPI](https://pypi.org/project/bitsandbytes/0.50.2/). Consultado 16/11/2026 Bogotá.

Es otro checkpoint/tamaño que el generador 3B, pero la misma familia Qwen: no independencia plena, ni garantía de mejor juicio por ser más grande. La cuantización del **juez** se mantendrá igual para ambos sistemas comparados y no se reportará como la mejora de eficiencia del generador. La carga real aún no se ha probado en T4; el código rechaza fallback a CPU o ausencia de capas Linear4bit reales.

La rúbrica completa está en [`judge_final.py`](judge_final.py), versión `final-judge-candidate-1.1`: 1 incorrecto/inventado; 2 error importante/explicación falsa o ausente; 3 parcialmente útil/incompleto; 4 sustentado con omisiones menores; 5 preciso/completo/con límites y fuentes. Se explicitó antes de inferencia la regla aprobada «sin explicación, nota máxima 2 aunque la respuesta corta sea correcta». No hay clamp programático: si el juez devuelve 5 en un caso así, se conserva el 5 y falla su calibración. Una abstención justificada puede obtener 5; una cifra correcta con explicación falsa no merece nota alta por coincidir casualmente.

## Anclas sintéticas para revisar antes de ejecutar

[`eval/calibration_review_v1`](eval/calibration_review_v1/REVISION_CALIBRACION.md) contiene veinte respuestas propuestas, no salidas del juez. Son diez pares buenos/malos sobre modalidad/tipo, cero adicional, contradicción, auditoría ausente, abstención injustificada, atribución falsa de campo, explicación vacía, cita que no respalda, acusación y negación. Datos ficticios, sin IDs ni gold de SECOP. Rango bueno 4–5; malo 1–2. Si el revisor discrepa, se corrige/versiona antes de medir, no se fuerza después la nota del modelo.

Las etiquetas `good`/`bad` y rangos solo se usan para auditoría posterior; **no entran en el prompt**. El payload del juez es una whitelist de pregunta, respuesta propuesta, fuentes y evidencia aritmética. Las fuentes son datos no confiables como instrucciones.

La revisión humana ya se recibió: el archivo original aprueba diecinueve ejemplos y deja uno pendiente. El usuario aprobó después empty_explanation_bad con la aclaración explícita del nivel 2. `human_approval.json` distingue las dos fuentes de aprobación y fija hashes de anclas, reglas, rúbrica y configuración. El original permanece intacto; su fecha declarada 16/11 se conserva, y el cierre posterior se registra con fecha del cliente 17/11. Después de GPU hará falta revisar razones reales: superar una regla numérica no asegura que el juez haya razonado correctamente. Las citas mantienen chunk_id exacto, sin colapsarlas por doc_id.

## Criterios fijados antes de observar puntuaciones

38 juicios: veinte principales mitigados; doce de sesgo sin mitigación (seis breves y seis verbosos); seis verbosos mitigados, emparejados con los seis breves ya evaluados entre los veinte principales. Cada llamada es independiente; orden breve/verboso alternado en la prueba inicial. La versión verbosa repite el mismo contenido cuatro veces, sin hechos nuevos.

Para superar el filtro automático:

1. 38/38 puntuaciones válidas tras como máximo un reintento de formato; todos los IDs/condiciones completos, sin duplicados.
2. Al menos 18/20 dentro del rango propuesto en los principales.
3. Ninguna respuesta deliberadamente mala recibe 4 o 5.
4. Seis pares mitigados válidos, con diferencia absoluta como máximo de un punto en cada par (por tanto media absoluta <=1).

Se informa antes/después aunque no mejore; no afirmar que desaparece el sesgo. Muestra sintética pequeña y conocida, no validación universal. Si falla, conservar la evidencia y detener la aceptación de calidad/eficiencia con ese juez. No volver a ejecutar seleccionando las notas más favorables.

## Ejecutable y pruebas actuales

[`ContractRisk_Final_Calibracion_Juez_Colab.ipynb`](ContractRisk_Final_Calibracion_Juez_Colab.ipynb) está preparado para sesión T4 separada, solo juez y no VLM/generador contractual. Primero aprobación humana y hashes, luego W&B y paquetes, un kernel CUDA NF4 pequeño y finalmente carga e inferencia. Si el kernel falla no se descarga/carga el checkpoint 7B. Guarda cada salida original y metadata, sin corrección de notas; finaliza W&B también al fallar. No envía preguntas/respuestas a W&B. Dependencias dedicadas en `requirements-calibration.txt`, sin cargar Chroma, reranker ni clasificador.

85 pruebas final CPU y 128 M3 pasan. Incluyen no fuga de expected/rangos, reintentos solo de formato, puntuaciones ausentes sin inventarlas, gate de calibración, paquete común de 22 entradas y bloqueo sin aprobación humana. Las dos nuevas regresiones comprueban que la regla de explicación vacía no reajusta notas y que las citas conservan chunk_id aunque compartan doc_id. Los tests de carga usan dobles sintéticos: **no prueban CUDA/NF4 real ni calidad del juez**.

## Próximo paso del equipo

No repetir los notebooks históricos buscando mejores notas. Ejecutar el [piloto por criterios y razonamiento](ContractRisk_Final_Juez_04_Razonamiento_Colab.ipynb): se detiene al primer fallo; solo si pasan los siete casos continúa hasta 38 juicios, sin repetir ni seleccionar las notas del piloto. Mantiene umbrales numéricos y añade coherencia interna, sin reajustar notas. Si supera regresión, revisar/ejecutar confirmación separada y auditar razones. Solo después se cierra el harness común y se compara con los [umbrales aprobados](EFICIENCIA.md). Estado local actual: 112 pruebas final y 128 M3 aprobadas; las cifras menores de las secciones anteriores describen etapas históricas.
