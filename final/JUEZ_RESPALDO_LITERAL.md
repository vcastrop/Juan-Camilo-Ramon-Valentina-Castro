# Juez 05: respaldo literal por campo y control de repetición

Estado 18/11/2026: preparado y probado en CPU, **no ejecutado con pesos**. [Notebook](ContractRisk_Final_Juez_05_Respaldo_Literal_Colab.ipynb), [configuración fija](judge_literal_config.json). No modifica las versiones anteriores, main ni Space.

## Cambio focalizado, no nueva selección de notas

Se conserva Qwen3-8B, revisión, NF4/FP16, semilla por caso, muestreo y presupuesto de 4096 tokens de la corrida 04. Cambian instrucciones, salida de respaldo y normalización; no se atribuirá una eventual mejora a un factor aislado. Se diseñó tras ver los fallos conocidos: ajuste post-hoc, no validación ciega.

El juez devuelve verificaciones, **soportes** por respuesta y explicación, nota y razón breve. Cada soporte identifica campo, chunk_id y cita literal, o null si no existe. El programa verifica que la cita sea contigua y exacta dentro de un fragmento citado por la salida y que el rótulo indicado figure en ella. **Eso no prueba que el fragmento responda a la pregunta ni que la explicación sea verdadera**: la pertinencia semántica sigue a cargo del juez y requiere auditoría humana. No se envía gold, rangos ni indicadores de acierto.

Si el modelo inventa una cita o se contradice, se conserva su nota original y se bloquea la aceptación. No se hace clamp ni reintento semántico. Solo se permite un reintento por estructura inválida. Una explicación falsa por atribución de campo merece 1–2 aunque la cifra corta sea correcta; no se aplica esa nota mediante código.

## Mitigación limitada de verbosidad

Solo en condiciones mitigadas se colapsa una respuesta o explicación formada por el **mismo bloque completo repetido literalmente**, separado por un espacio. No se resumen frases, no se eliminan paráfrasis ni contenido diferente, no se normalizan números, y las fuentes/citas no cambian. Se registran hashes y longitudes antes/después, sin reemplazar el registro original. Antes de mitigación el texto repetido se entrega intacto.

La comprobación con tokenizer real dio 38/38 entradas nativas y los seis pares mitigados tienen idéntica entrada al modelo. Con la misma semilla por caso, una eventual igualdad de notas demuestra como máximo invarianza de esta transformación; **no ausencia general de sesgo de longitud**. Repeticiones parciales, paráfrasis y verbosidad con contenido diferente no se corrigen.

## Piloto y aceptación

Nueve casos: los siete del protocolo 04 más `attribution_bad` y `accusation_good`. Son anclas sintéticas ya aprobadas; se amplía el piloto para cubrir fallos observados, no se cambian rangos. Se detiene al primer fallo. Si pasan los nueve, se reutilizan sus notas y se completa la misma agenda de 38 juicios, sin escoger una de varias ejecuciones.

Permanecen 38 válidos, al menos 18/20 en rango, ningún malo principal con 4–5 y máximo 1 de diferencia por par mitigado. Se mantienen coherencia interna y se añade respaldo literal válido, comprobado de nuevo al recalcular. Superar regresión conocida no sustituye revisión humana de razones ni la confirmación separada de doce ejemplos nuevos, todavía sin aprobación/ejecución.

## Ejecución

Abrir una sesión nueva Colab T4, habilitar acceso al secreto WANDB_API_KEY y ejecutar en orden. Descargar `contractrisk_final_juez_literal_resultados.zip` y el notebook con salidas incluso si el piloto se detiene. No repetir para seleccionar notas favorables. No se guardan textos privados de razonamiento. W&B registra latencia/estado, no los contenidos; la cuantización del juez no cuenta como eficiencia del generador contractual.

122 pruebas final y 128 M3 aprobadas localmente. Incluyen normalización conservadora, no fuga de gold, conservación de nota con cita inventada, reintento solo de formato, detección de cita/campo inválidos y recálculo del filtro. No demuestran calidad semántica ni GPU.
