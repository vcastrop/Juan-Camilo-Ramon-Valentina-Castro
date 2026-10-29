# Agente de desarrollo v3 — implementación, no resultados finales

## Necesidad y alcance

El gold revisado incluye comparaciones de valores; una resta exacta requiere operandos trazables. La herramienta `diferencia_valores_contratos` consulta dos valores del corpus público congelado y calcula la diferencia absoluta con Decimal. No recibe referencias gold y no interpreta el resultado como sobrecosto. Sustituye la propuesta inicial genérica de consultar una ficha por una operación más acotada y verificable.

Código: `contract_tools.py`, `rag_agent.py`, `structured_output.py`. Esquema JSON de entrada en `TOOL_SCHEMA`: exactamente id_a e id_b, formato CO1.PCCNTR.número, distintos y explícitos en la pregunta. Solo lee documentos precargados del corpus: no admite rutas, URLs ni código del modelo. Retorna ok, valores_cop, absolute_difference_cop, operation, contexts, error y latency_seconds. Los contextos conservan URL, ID y offsets exactos del campo fuente; la operación es evidencia derivada, no texto atribuido al contrato.

## Decisión y límites

El modelo decide action=tool o action=answer. No hay una regla que fuerce llamadas según un ID gold. Hasta tres decisiones del controlador y una generación final; decisiones inválidas consumen un paso y se conservan. Se acepta un objeto JSON con cerco Markdown opcional, pero no claves duplicadas, múltiples objetos ni constantes no finitas. Se bloquean llamadas repetidas. Herramienta de lectura local con presupuesto cooperativo de dos segundos: no es un cancelador de llamadas de red, pues no hay red en la operación. Errores no producen operandos ficticios ni citas.

Todas las decisiones crudas, parseos, argumentos, resultados y errores se guardan en tool_trace. La respuesta final conserva el contrato de BasicRAG. El prompt base v3 es común a las cuatro variantes; el controlador del agente es adicional y se declara. El prompt v2 y sus corridas históricas no se modifican. El v3 refuerza distinción modalidad/tipo/objeto/duración y abstención, pero su calidad aún NO está demostrada con el modelo real.

El agente agrega evidencia de herramienta al contexto. Por ello su presupuesto total de evidencia no es idéntico al del RAG sin herramienta: debe declararse al interpretar mejoras. Las futuras métricas de sustento deben evaluar también la operación con sus operandos, no solo los chunks iniciales.

## Prueba de desarrollo preparada

En T4, con las mismas dependencias de development v2:

```bash
python -m pip install -r m3/requirements-development-v2.txt
python -m unittest discover -s m3/tests -v
python -u m3/run_agent_development.py --output desarrollo_v3_resultados
```

El directorio de salida debe ser nuevo. Cuatro variantes y ocho preguntas: cuatro modalidades de desarrollo, dos diferencias de valores sobre esas fichas y dos ausencias documentales. No se ejecuta ni modifica el gold. Se guardan 32 registros si la ejecución completa; su existencia no implica 32 aciertos. Las etiquetas de desarrollo se incorporan después de inferencia, únicamente para inspección. No se ha ejecutado esta prueba con modelos reales todavía.

Revisión requerida después de Colab: dos cálculos con llamadas efectivas y operandos correctos; al menos una respuesta sin llamada; errores y llamadas innecesarias; abstención frente a evidencia no pertinente; calidad de las citas. Las pruebas unitarias usan generadores simulados: comprueban el flujo, no que Qwen tome buenas decisiones.

## Pendientes de entrega

Juez independiente y calibración, dominio y RAGAS, configuración final congelada, corrida comparable sobre gold y análisis. No usar esta ejecución de desarrollo como scorecard final ni declarar que una prueba unitaria satisface las trazas reales de la rúbrica.
