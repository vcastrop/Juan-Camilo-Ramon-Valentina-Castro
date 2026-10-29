# Cierre auditado tras integrar el trabajo del compañero

## Qué está integrado y qué evidencia sigue vigente

Los cuatro commits del bundle se integraron conservando el historial local v6 y sin modificar main. La corrida final corresponde al código `6026ac4`; sus 28 hashes de fuentes coinciden. Sus respuestas, notebook, logs, métricas y auditoría permanecen intactos en `results/final_m3/`. V6 es un candidato de desarrollo no adoptado, no una mejora final demostrada.

## Correcciones posteriores, identificadas como tales

- `audit_rules_m3.py`, versión 1.1: cifras como tokens completos, rechazo de negaciones explícitas acotadas, validación estructural y detección de insinuaciones como «sugiere una posible irregularidad». No es un verificador semántico universal.
- `rescore_audit_m3.py`: aplica las mismas reglas a las 72 respuestas guardadas. No vuelve a generar, no altera el juez ni las latencias. Exige cobertura completa por variante y rechaza duplicados/preguntas distintas. Resultados en [audit_m3_1_1](results/audit_m3_1_1/RESUMEN.md), con hashes y diferencias por caso.
- Solo cambian dos pases: m3_009 del avanzado y del final. El dominio final pasa de 5/12 a **4/12**, y el avanzado de 4/12 a **3/12**. Cobertura léxica y notas del juez permanecen iguales. La regla de cifras se corrige aunque no cambie los valores de esta corrida.
- `ragas_audit_m3.py`: conserva IDs y decimales al separar afirmaciones, conserva afirmaciones cortas, rechaza sí/no ambiguos y marca la métrica de un caso como ausente si falla un veredicto necesario. No descarta los fallos para mejorar el promedio.
- La adaptación usa precisión sensible al rango y recall por afirmación. Es una adaptación de S10, no una reproducción literal de todas sus fórmulas. Se conserva la política original de excluir abstenciones de faithfulness para aislar esta reparación; esa política es una limitación, pues una abstención también puede contener afirmaciones.

## Cómo continuar

1. Ejecutar `ContractRisk_M3_Auditoria_Colab.ipynb` con GPU T4 y el paquete de código de auditoría. Solo repite RAGAS sobre las 36 respuestas guardadas de ingenuo, avanzado y final. No vuelve a generar ni recuperar respuestas.
2. Devolver el ZIP, incluso si falla. Conserva metadatos, hashes, juicios originales y errores. No afirmar que existe un scorecard RAGAS 1.1 hasta revisar esa ejecución.
3. Revisar manualmente los juicios, especialmente m3_009 y m3_012. Un parser correcto no convierte al juez Qwen en una referencia fiable. El juez del harness original se conserva, no se reemplaza por la corrección de etiquetas de M2.
4. Confirmar por los autores la contribución humana en «Uso de IA» del README. No puede completarse inventando revisiones.
5. Revisar la rama, publicar y abrir/revisar PR. No fusionar main automáticamente.

## Límites de las conclusiones

La mejora de recuperación de fichas es real en esta muestra; no prueba que todos los campos necesarios estén presentes. La herramienta recupera operandos y calcula. La cobertura automática de hechos no es porcentaje de respuestas completamente correctas. Sigue habiendo una auditoría inventada, abstención 0/2 en avanzado/final y un juez que premia un error. El gold ya fue evaluado e inspeccionado: cualquier ajuste posterior debe declararse post-hoc y no presentarse como nueva validación independiente. Son 12 casos, no evidencia de desempeño general en SECOP ni de detección de corrupción.

Pruebas locales tras integrar y corregir: **113 aprobadas**. Esto verifica código y regresiones, no calidad del modelo. La reevaluación GPU está pendiente.
