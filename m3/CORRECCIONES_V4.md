# Correcciones de desarrollo v4

Estado: implementadas y probadas localmente; calidad con modelo real pendiente. Se preservan v2/v3 y su evidencia, sin modificar gold ni main.

## Causa observada y cambio

| Fallo v3 | Evidencia | Cambio v4 |
|---|---|---|
| JSON final incompleto | El modelo copia objetos completos dentro de citas y la salida termina en mitad de ellos | Mensajes compactos con chunk_id/doc_id/text, cálculos sin duplicar contextos, ejemplo explícito de citas como strings, límite de 512 tokens y registro de tokens/EOS |
| Formatos alternativos del controlador rechazados | action contiene el nombre de la herramienta o answer añade result | Normalizador limitado a esas dos variantes inequívocas; conserva original y regla aplicada; nunca interpreta prosa ni inventa IDs |
| Llamadas innecesarias y repetidas | Cinco consultas de un contrato intentan usar una operación de dos contratos | Controlador ve pregunta/IDs/esquema y error anterior, no historial y fragmentos repetidos; ejemplos sintéticos de llamada/no llamada; termina tras éxito; sigue validando argumentos |
| Confusión tipo/modalidad y auditoría inventada | Evidencia correcta ignorada o usada para inferir un informe ausente | Prompt común más breve y explícito, ejemplo sintético de campos distintos y prohibición de inferir auditoría de estado/valor/fechas; eficacia pendiente de T4 |
| Notebook completed pese a errores por caso | El runner guarda parse_error y continúa | Se mantiene registro de fallos; añade primer intento válido, todos los intentos y observaciones de generación. Completed significa bucle terminado, no calidad aprobada |

El límite de 320 tokens de v3 pudo causar truncamiento, pero no había registro de terminación para afirmarlo de manera concluyente. V4 registra output_tokens, ended_with_eos y reached_token_limit. Aumentar el límite no garantiza corrección; la reducción de payload y el esquema explícito abordan el problema de raíz.

## Comparabilidad y protección contra resultados artificiales

- Cuatro variantes comparten generador/revisión, prompt base v4, límite de 512 tokens y protocolo de salida. Semilla 42, top-k 3, chunks 220/30 y pool 12 permanecen iguales.
- Un solo reintento si falla el formato/esquema/citas permitidas, sin leer gold ni puntuación. Un JSON válido pero semánticamente incorrecto NO se reintenta ni se sustituye. Se informarán éxito inicial y final por separado.
- La herramienta devuelve cifras exactas; no se reemplaza automáticamente la cifra escrita por el modelo. Una discordancia sigue siendo error de generación que debe evaluarse.
- El controlador sigue decidiendo. No se fuerza una llamada según la etiqueta esperada. Terminar después de un cálculo exitoso es una regla del flujo de una herramienta, no una decisión atribuida al modelo.
- El agente recibe contexto adicional de herramienta y tarda más por el controlador. Se conserva esa diferencia para análisis, no se presenta como comparación de costo idéntico.
- Las ocho preguntas son de desarrollo; el gold final no se ejecuta ni modifica. Los ejemplos sintéticos del prompt no contienen respuestas gold.

## Ejecución

Usar `ContractRisk_M3_Desarrollo_v4_Colab.ipynb` con el ZIP v4 en una sesión T4. Ejecuta 50 pruebas y `run_development_v4.py`; conserva ZIP/notebook, incluso si hay errores. Se esperan 32 registros de ejecución, no 32 aciertos garantizados. Revisar números, abstenciones, citas, llamadas y primer intento antes de congelar configuración.

Pendientes de entrega: validar v4 con modelos reales, calibrar juez independiente y verbosidad multicaso, completar dominio/RAGAS/harness final y correr las cuatro variantes sobre gold. Las pruebas locales verifican reglas de software, no la comprensión del modelo ni el cumplimiento completo de M3.
