# Prueba controlada después de la regresión v4

Estado: implementada y probada con dobles locales; inferencia en T4 pendiente. No es el scorecard final, no es evaluación del retriever y no es calibración del juez.

## Hipótesis y condiciones fijadas antes de ejecutar

La evidencia v4 mostró omisión de abstencion, copia de un marcador como cita, llamadas inapropiadas y cifras alteradas, sin alcanzar el límite de tokens. Se separan dos factores mediante tres condiciones:

1. Qwen2.5-1.5B-Instruct con protocolo v4 como referencia.
2. El mismo modelo con protocolo candidato v5.
3. Qwen2.5-3B-Instruct con el mismo protocolo candidato v5.

La comparación 1/2 explora el protocolo; 2/3 explora el modelo bajo el mismo protocolo. No reproduce el harness v4 completo: aquí se entrega contexto sintético fijo y se prueba enrutamiento aislado (máximo un reintento de formato), no un bucle completo de agente/retriever. No atribuir resultados a mejoras de recuperación.

V5 elimina el ejemplo con marcador de cita, proporciona esquema completo con las cuatro claves y citas permitidas, y muestra esquema/error/salida previa durante la reparación. No inventa campos, notas ni citas para completar respuestas. El controlador recibe pregunta e IDs, con instrucciones más cortas; aún debe escoger la acción él mismo.

## Casos y datos

Diez casos sintéticos, creados para diagnóstico y separados de IDs y preguntas gold: seis respuestas (dos modalidades, dos ausencias documentales, dos resultados numéricos) y cuatro decisiones (dos herramientas y dos sin herramienta). Las ausencias están explícitas en esta prueba sencilla; superarla no demuestra abstención robusta en las fichas reales. No se consultan SECOP ni el gold para generar los casos.

Los tres brazos usan las mismas preguntas/contextos, semilla 42, inferencia greedy y máximo 512 tokens. Un único reintento solo por error de formato; nunca por nota baja o error semántico. Los controles esperados permanecen fuera del mensaje del modelo y se aplican después. La prueba de selección no ejecuta una herramienta externa: verifica nombre y argumentos elegidos contra IDs de la pregunta. Las funciones de cálculo ya tienen evidencia separada de ejecución real.

## Medidas y lectura

Se conserva respuesta cruda de cada intento, normalización de decisiones, errores, tokens, EOS, latencia, modelo/revisión, hashes, versiones, memoria máxima y carga. Resumen: formato inicial/final, comprobaciones mecánicas y decisiones correctas, con denominadores. No hay puntajes de juez ajustados ni sustitución por accuracy.

Una comprobación mecánica es limitada: presencia de un número correcto no prueba toda la explicación; abstencion=true puede acompañarse de una afirmación sin sustento. Revisar todas las explicaciones antes de aceptar un candidato. No se selecciona automáticamente un modelo por el mayor porcentaje. Si persisten errores, informar resultados negativos y decidir explícitamente qué puede congelarse; no encadenar corridas hasta obtener una favorable.

## Modelos y recursos

- Modelo actual: revisión `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- Candidato 3B: revisión `aa8e72537993ba99e69dfaafa59ed015b17504d1`, comprobada en la [API oficial del repositorio](https://huggingface.co/api/models/Qwen/Qwen2.5-3B-Instruct). La [ficha del modelo](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) documenta uso con Transformers y licencia qwen-research; no atribuirle Apache ni redistribuir sus pesos dentro del proyecto.
- Se descargan pesos públicos y se cargan modelos uno por vez, liberando GPU entre ellos. No usa claves de servicios pagos. La compatibilidad/memoria se verificará realmente en T4; fallos de descarga/carga se guardan y no se simulan resultados.

## Ejecutar

Abrir `ContractRisk_M3_Prueba_Protocolo_Colab.ipynb` en sesión T4 nueva y subir `contractrisk_m3_protocolo_codigo.zip`. Ejecutar en orden. Descargar ZIP final y notebook ejecutado. Si falla un modelo o una celda, conservar logs con la última celda. La metadata distingue completed, completed_with_errors y failed.

Si se adopta un modelo/protocolo diferente después de esta prueba, las cuatro variantes finales deben ejecutarse de nuevo con esa misma configuración. Calibración de juez, dominio, RAGAS y revisión final continúan pendientes.
