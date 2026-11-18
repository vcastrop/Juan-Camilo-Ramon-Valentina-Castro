# Juez por criterios y razonamiento — ensayo preparado

Estado 18/11/2026: código y tokenización comprobados en CPU; **sin inferencia GPU ni juicio aprobado**. [Notebook para Colab](ContractRisk_Final_Juez_04_Razonamiento_Colab.ipynb), [configuración fija](judge_reasoning_config.json).

## Qué cambia y por qué

Qwen/Qwen3-8B, revisión `b968826d9c46dd6066d109eabc6255188de91218`, NF4 con cómputo FP16 y doble cuantización. Es público y Apache-2.0 según su [ficha oficial](https://huggingface.co/Qwen/Qwen3-8B). Se usa modo de razonamiento con muestreo recomendado por el fabricante: temperatura 0,6; top-p 0,95; top-k 20; min-p 0. No se usa greedy, desaconsejado en esa ficha para este modo.

Se cambian conjuntamente modelo, protocolo y decodificación: una eventual mejora no se atribuirá a un solo factor. Sigue siendo familia Qwen, como el generador contractual, por lo que no representa independencia plena. La viabilidad real en T4 debe comprobarse, no se deduce de la prueba CPU.

El presupuesto máximo del proyecto es 4096 tokens, inferior al recomendado por el fabricante para tareas largas. Si se agota o no se cierra el bloque de razonamiento, se registra una generación incompleta y se detiene el piloto; no se interpreta como una nota válida. Puede tardar más que los ensayos anteriores.

## Evaluar evidencia, no fabricar la nota

Antes de la nota, el modelo devuelve verificaciones separadas de respuesta, explicación, citas, abstención y acusación sin respaldo. Solo recibe pregunta, salida propuesta, fragmentos y evidencia de herramienta; no recibe gold, rangos aprobados ni indicadores de acierto. Mantiene la rúbrica aprobada 1–5, incluida explicación ausente con máximo 2.

El programa conserva la nota original incluso si contradice esas verificaciones. La incoherencia hace fallar la calibración; **no limita, reemplaza ni reajusta puntuaciones**. Solo hay un reintento para formato inválido, nunca para obtener una nota preferida. El razonamiento privado no se decodifica ni conserva: se guardan conteos/hashes de tokens y el JSON final público sin editar, con su justificación breve.

## Piloto con parada temprana

Orden fijado: `short_good`, `short_bad`, `number_bad`, `conflict_good`, `conflict_bad`, `empty_explanation_bad`, `citation_bad`. Son ejemplos sintéticos ya aprobados, no preguntas gold del conjunto final. Deben pasar los siete dentro de su rango, con formato válido y verificaciones coherentes. Se detiene al primer fallo; los restantes figuran como **no ejecutados**, no como fallidos.

Si supera el piloto, sus siete notas se reutilizan sin repetirlas ni seleccionarlas. Continúa hasta completar los mismos 38 juicios: veinte principales, doce de sesgo inicial y seis verbosos mitigados. Se mantienen 38 válidos, al menos 18/20 en rango, cero malos con 4–5 y diferencia máxima de 1 en cada par mitigado. Se añade coherencia interna de las verificaciones. La semilla por ejemplo es la misma entre variantes, sin garantizar identidad entre plataformas ni eliminar variabilidad del muestreo.

Superar esta regresión conocida **no valida todavía al juez**: siguen pendientes la aprobación humana de los doce casos nuevos de confirmación, su ejecución y una auditoría de las razones. No se repiten corridas para escoger notas favorables.

## Comprobaciones y ejecución

[Diagnóstico de tokenización](evidence/reasoning_tokenizer_cpu/diagnostic.json): 38/38 entradas equivalentes al template nativo, con cambio de modo de razonamiento reconocido y token de cierre 151668. No se cargaron pesos ni se usó GPU: demuestra entrada correcta, no buen juicio. Las pruebas unitarias emplean también dobles sintéticos.

Abrir el notebook en una sesión nueva de Colab T4, habilitarle acceso al secreto `WANDB_API_KEY` y ejecutar de arriba abajo. Descargar ZIP y notebook con salidas incluso si el piloto se detiene. No cambiar versiones ni volver a ejecutar buscando aprobación. El script escribe en una carpeta nueva; no modifica main, el Space ni las corridas anteriores. W&B registra latencia/estado, no contenidos de preguntas o respuestas. La cuantización de este juez no cuenta como la mejora de eficiencia del generador contractual.
