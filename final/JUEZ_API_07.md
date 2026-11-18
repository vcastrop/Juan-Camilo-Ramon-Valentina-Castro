# Juez API 07 — calibración sintética preparada

Actualización de ejecución: [el intento 07 recibió HTTP 503 sin notas](evidence/api_07/ANALISIS.md). No repetir este notebook. Después de auditarlo se preparó una [única recuperación 08](JUEZ_API_08_REINTENTO.md), con las marcas y reserva originales intactas. La preparación siguiente documenta el protocolo original, no una calibración aprobada.

Estado 18/11/2026: cliente REST, runner, notebook y pruebas con transportes simulados preparados. **Sin llamadas de inferencia desde este entorno, sin API validada ni calidad aprobada.** El usuario confirma que guardó GEMINI_API_KEY en Colab; no se conoce su valor. [Notebook](ContractRisk_Final_Juez_07_API_Colab.ipynb), [configuración](gemini_calibration_config.json), [política de presupuesto](api_budget_policy.json).

## Modelo y procedimiento fijados antes de observar notas

Candidato gemini-3.8-flash según [ficha oficial](https://aistudio.google.com/docs/models/gemini-3.8-flash), consultada el 18/11. Primero models.get comprueba nombre y métodos; no hay fallback a otro modelo. Cada respuesta debe informar modelVersion de la misma familia y permanecer idéntica durante la corrida. Es un servicio gestionado, no un hash de pesos descargables; una semilla solicitada no garantiza identidad entre plataformas o fechas.

Se usa REST generateContent, JSON Schema con puntaje entero 1–5 y razon, maxOutputTokens 4096 y thinkingLevel HIGH sin devolver pensamientos. No se envían temperature/topP/topK: la [referencia actual](https://aistudio.google.com/api-reference/generate-content) indica que el modelo ignora esos parámetros en esta generación. Se conserva solo texto final público y metadata de uso/versiones; nunca pensamientos ni firmas internas. No hay herramientas, búsquedas, archivos subidos, caché explícita ni SDK con retries automáticos.

Rúbrica aprobada final-judge-candidate-1.1 y whitelist de pregunta, respuesta propuesta, fuentes y cálculo válido. No expected, rangos, comparación de etiquetas, confianza ni resultado automático. Se vuelve al esquema simple original del juez, no al protocolo de soportes que falló con Qwen. Cambian modelo/proveedor y protocolo respecto a esa última corrida; no se atribuirá una mejora a un único factor ni se mezclan notas históricas.

## Piloto y regresión

Nueve anclas ya aprobadas, en orden: attribution_bad, attribution_good, short_good, short_bad, number_bad, conflict_good, conflict_bad, empty_explanation_bad, citation_bad. Cada una debe quedar en su rango; parada al primer fallo, empezando por el defecto que rechazó Qwen. Es un filtro sobre ejemplos conocidos tras desarrollo, no una validación ciega.

Si pasan, sus nueve notas se reutilizan y se completa la agenda de 38: veinte principales mitigados, doce de sesgo previo y seis verbosos mitigados. No se normaliza el texto en este candidato; la mitigación es la instrucción original contra verbosidad. Se mantienen 38 válidos, al menos 18/20 en rango, cero malos principales con 4–5 y diferencia máxima de 1 por cada par mitigado. No se transforma una nota equivocada ni se reintenta por desacuerdo semántico.

Un único reintento por JSON inválido; ninguno por red, cuota o truncamiento. Cualquier fallo de API/generación/formato sin nota detiene toda la agenda, conserva parciales y no se interpreta como mal juicio de casos no ejecutados. Regresión aprobada todavía requiere auditoría humana de motivos y confirmación separada de doce ejemplos nuevos revisados. Ese conjunto no se ejecuta aquí.

## Gratuito y presupuesto

Antes de ejecutar, el titular debe comprobar que el proyecto de su clave muestra **Free Tier y no tiene facturación activada**, y escribir GRATUITO en el notebook. Esto es una declaración del titular: el programa no puede detectar por sí mismo el plan de facturación. Si el proyecto está pagado o no puede verificarse, no ejecutar ni escribir la confirmación; consultar. El permiso de USD 5 no activa un modo pagado en este runner.

La clave y WANDB_API_KEY se leen de secretos de este notebook. No pegarlas en celdas. Se monta Drive para mantener `/MyDrive/ContractRisk_final_budget/`: registro común de reservas y marca exclusiva de este experimento. No contienen claves ni prompts. La marca bloquea repetir incluso desde otra sesión; no borrarla sin revisar un resultado parcial. No reiniciar el registro para eludir el límite.

Se usa la tarifa pública de referencia (USD 0,75/M entrada, USD 3,75/M salida incluidos pensamientos), con revisión obligatoria después del 20/11 UTC. El cliente reserva usando el límite completo de salida anunciado del modelo y el tope pequeño de entrada, a la tarifa mayor; countTokens solo se trata como estimación. Tras recibir uso válido se registra una estimación conservadora usando todos los tokens a tarifa de salida, no una factura. Un timeout mantiene la reserva. Techo total USD 5 y techo adicional USD 1 de estimación para esta calibración. Si se supera una reserva, el registro se bloquea. Impuestos, precios cambiantes y uso externo del proyecto no quedan garantizados por este registro local: por eso se mantiene **modo gratuito confirmado**, no facturación automática.

## Instrucciones

1. Abrir notebook 07; basta runtime CPU, no hace falta T4.
2. Habilitar acceso de ESTE notebook a GEMINI_API_KEY y WANDB_API_KEY.
3. Ejecutar en orden, autorizar Drive para el registro y confirmar únicamente si el proyecto es gratuito sin facturación.
4. Conservar ZIP y notebook con salidas incluso si se detiene. Si hay 403/404/429, no cambiar modelo, activar pagos o repetir automáticamente.

Archivo generado: contractrisk_final_juez_api_resultados.zip. W&B registra latencia/validez, no preguntas/respuestas. Main y Space no se modifican. Las pruebas locales usan respuestas simuladas: no prueban acceso real, ausencia de cobros del proveedor, calidad ni velocidad de la API.
