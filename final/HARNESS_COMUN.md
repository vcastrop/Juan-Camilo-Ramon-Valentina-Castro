# Harness común candidato — avance de implementación

Estado 18/11/2026: [common_harness.py](common_harness.py) implementado y probado con casos sintéticos en CPU. **No hay nueva ejecución de los 22 casos con modelos, protocolo final congelado ni aceptación de calidad.** No sustituye las tablas históricas M3.

Verificación local de esta etapa: 151 pruebas final y 128 M3 aprobadas. Doce pruebas iniciales del harness y dos de robustez posteriores cubren frontera sin gold, números/negaciones, citas, errores, filas ausentes, tipos malformados e invarianza sin confundirla con corrección.

## Separación de responsabilidades

load_common comprueba hashes canónicos de entradas/referencias, IDs y hashes de imágenes, y rechaza rutas fuera del repositorio. infer entrega al sistema únicamente pregunta e imagen; las referencias no cruzan esa frontera. Cada error permanece en el denominador, identificado sin copiar mensajes de excepción potencialmente sensibles.

evaluate calcula diagnósticos después de la inferencia y entrega al juez una whitelist sin expected, criterion, comparaciones de acierto ni rangos. Las notas brutas se conservan incluso cuando contradicen las coincidencias automáticas. No se inventan notas si el juez no está disponible o devuelve formato inválido.

## Tres dimensiones, sin aparentar cierre

1. **Automática:** cobertura literal conservadora de hechos en respuesta, no en explicación. Números completos con límites y separadores de miles inequívocos; negación próxima, sin rescate por paráfrasis. Una explicación que menciona un hecho no rescata una respuesta incorrecta o una abstención indebida. Se registra existencia/trazabilidad de citas y extracción visual por campo, por separado.
2. **Juez:** media bruta experimental de notas válidas, con conteo de juicios presentes. Sin juez validado no se denomina calidad aprobada.
3. **Dominio:** permanece null/pending hasta cerrar la definición y enlazar evidencia real de calibración/confirmación. El chequeo automático se llama automatic_domain_checks_pass, **no domain_pass**. No se convierte cobertura literal en cumplimiento.

Las cifras/textos pueden aparecer en una respuesta falsa; una cita existente no garantiza respaldo; la negación es aproximada y no se comprenden paráfrasis. Invarianza compara salidas estructuradas de dos entradas: ambas pueden ser igualmente incorrectas. Los dos pares tienen un indicador separado de coincidencia de los chequeos automáticos. Estos límites no se ocultan ni se tratan como verdad semántica.

## Reutilización

Un sistema debe implementar predict(question, image=None) y devolver un registro con output (respuesta, explicacion, citas, abstencion), contexts y, si corresponde, tool_trace/visual. Un baseline sin visión debe declarar su limitación y producir su salida real; no recibirá transcripción gold ni se quitarán sus imágenes del denominador.

harness(eval_set_folder, system, judge=None) carga el paquete, ejecuta, evalúa y devuelve predicciones, detalle y scorecard candidato. Guardar resultados con configuración/hashes y mediciones CUDA reales será responsabilidad del runner comparativo todavía pendiente. La latencia CPU de pruebas unitarias no es latencia de los modelos ni memoria de eficiencia.

## Pendientes para cerrar

- Adaptadores comparables QA sin RAG, M3, base visual FP16 y generador NF4.
- Congelar política de controles/daño y dominio, enlazando juez realmente validado.
- Runner con warm-up, sincronización GPU, memoria pico y mismas condiciones; no fabricar valores de CUDA.
- Ejecutar 22 casos por perfil y ablación; repetir controles de abstención/adversariales/invarianza en versión eficiente.
- Guardar y recalcular tabla evolutiva antes de aplicar efficiency_acceptance.py.
