# Integración 3B/v5 y calibración del juez

Estado: corrida real de integración/calibración ejecutada y auditada el 29/10/2026. [Resultados, originales y limitaciones](evidence/integration_v5/ANALISIS.md). Ejecución técnica completada, calidad no aprobada: fallos de abstención y del juez; mitigación sin mejora. No es cierre de M3. [Guía para continuar](CONTINUAR_TRABAJO.md).

## Sistema integrado

`systems_v5.py` y `agent_v5.py` reutilizan exactamente ANSWER_V5 y ROUTER_V5 de la prueba sintética, sin alterar sus instrucciones ni completar salidas por reglas. El generador es Qwen2.5-3B-Instruct, revisión aa8e72537993ba99e69dfaafa59ed015b17504d1, para las cuatro variantes. Embeddings, reranker, corpus, chunks 220/30, top-k 3 y pool 12 siguen fijados. La selección se justifica en [la evidencia de protocolo](evidence/protocol_probe/ANALISIS.md), incluyendo su fallo de clausulado.

El control sin RAG es un control generativo adaptado a QA; no se presenta como RoBERTalex de M2. El agente decide llamadas, mantiene máximo de tres pasos, valida argumentos y conserva trazas/errores. Comparte el protocolo final con las demás variantes; el contexto adicional de herramienta y la latencia del controlador se declaran, no se ocultan.

`run_integration_v5.py` conserva las mismas ocho preguntas reales de desarrollo: 32 predicciones. El gold de 12 casos revisados permanece sin ejecutar. Se registran prompt/modelos/revisiones/hashes, hardware, tiempos y primer intento/final. Ninguna respuesta se modifica por coincidir o no con una referencia.

## Calibración del juez y verbosidad

`calibration_v1.py` crea 12 casos SINTÉTICOS (no anotados independientemente por humanos): cuatro respuestas sustentadas, cuatro incorrectas y cuatro abstenciones justificadas. Una respuesta incorrecta carece de explicación, para comprobar el problema señalado por el profesor. Los rangos esperados [4,5] y [1,2] son expectativas diagnósticas propuestas antes de ejecutar, no notas humanas ni reglas que sustituyan al juez.

Para cada caso se crea una versión extensa repitiendo literalmente respuesta/explicación cuatro veces, sin añadir afirmaciones. Esta prueba aísla repetición/longitud; no cubre todos los estilos posibles de verbosidad natural. Se evalúan las dos versiones antes y después de la instrucción de mitigación: 12 x 2 x 2 = 48 juicios. Orden breve/extenso alternado por caso, cada llamada sin historial de conversación ni notas previas.

El juez recibe pregunta, respuesta/explicación/citas/abstención y contexto, nunca grupo, rango esperado ni indicador de corrección. Guarda ambas salidas si falla el primer formato; no reintenta por una nota baja y no inventa notas cuando falla. Promedios entre notas válidas se acompañan de cobertura, fallos y denominadores. Diferencias antes/después se reportan con signos y valores absolutos, sin proclamar mitigación efectiva antes de verlas.

El generador y juez comparten modelo/revisión pero usan instrucciones y llamadas separadas. No implica independencia estadística ni elimina autopreferencia. Esta limitación se mantendrá en el informe. Si el juez puntúa bien respuestas malas o elogia explicaciones vacías, no se sustituirán sus notas con reglas: se reportará y corregirá antes del scorecard final.

## Revisión posterior obligatoria

1. Verificar que los dos cálculos reales terminan con cifras correctas y citas a ambos operandos, además de llamadas correctas.
2. Revisar decisiones sin herramienta y abstenciones. Una afirmación de ausencia de documento no debe convertirse en afirmar que el hecho nunca ocurrió.
3. Revisar cada razón del juez, especialmente errores, explicación vacía y abstenciones; registrar discrepancias con expectativas.
4. Comparar pares breves/extensos en ambas condiciones, sin ocultar parseos fallidos. Cero diferencia por puntaje constante NO demuestra buen juez.
5. Solo después decidir la configuración final. Faltan métricas de dominio, RAGAS, harness final, corrida gold y reporte/entrega.

## Ejecutar y devolver

Notebook: `ContractRisk_M3_Integracion_v5_Calibracion_Colab.ipynb`. ZIP de código: `contractrisk_m3_integracion_v5_codigo.zip`. Ejecutar desde sesión T4 nueva, celdas en orden. Devuelve notebook con salidas y ZIP completo. Contendrá predictions.jsonl, calibration_cases.json, calibration.jsonl, calibration_summary.json, chunks.jsonl, metadata.json y logs si todo el flujo finaliza.

Metadata marca quality_status=requires_manual_review incluso cuando status=completed. No hay métricas finales anticipadas ni declaración de revisión humana ficticia. Main no se modifica.
