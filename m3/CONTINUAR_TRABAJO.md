# Continuar ContractRisk M3 — guía de traspaso

Actualización: 29 de octubre de 2026. Rama de trabajo: `Entrega/contractrisk-m3`. No trabajar directamente en `main`. Estado de código y evidencia auditado: `f64ae5b`; los commits posteriores de este traspaso añaden documentación, no cambian el modelo.

## Actualización: corrida final hecha

La evaluación final sobre el gold ya se ejecutó y está auditada: ver [README](README.md#resultados) y [results/final_m3/ANALISIS.md](results/final_m3/ANALISIS.md). Pendientes: confirmar Uso de IA, publicar y entregar. Fallos conocidos para M4/M5: válvula de escape con contexto pertinente, explicaciones de cálculo, juez 3B. Lo que sigue en este archivo describe el estado anterior a la corrida final.

## Leer primero

1. [Checklist canónico](CHECKLIST.md): estado vigente al principio y fases A–L. Avance estimado 60% de M3; NO es una calificación ni un cierre.
2. [Auditoría de integración v5](evidence/integration_v5/ANALISIS.md): resultados y fallos reales; ZIP y notebook ejecutado en esa misma carpeta.
3. [Diseño de integración](INTEGRACION_V5.md), [juez](JUEZ_M3.md) y [decisiones iniciales](DECISIONES_INICIALES.md).
4. Solicitar al equipo la guía oficial `STAI_M3_Asignacion_RAG_agentico.pdf` y materiales S07/S08/S10. No asumir que están publicados en este repositorio; el checklist resume sus requisitos, pero no reemplaza la guía.

## Obtener el trabajo

En un directorio nuevo, con Git instalado:

```powershell
git clone --branch Entrega/contractrisk-m3 --single-branch https://github.com/vcastrop/Juan-Camilo-Ramon-Valentina-Castro.git contractrisk-m3
cd contractrisk-m3
git status
git log -3 --oneline
```

Para no pisar trabajo simultáneo, crear una rama propia desde este punto, por ejemplo:

```powershell
git switch -c trabajo/m3-continuacion
```

Coordinar quién trabaja en cada archivo. Con permiso WRITE se puede publicar esa rama y abrir PR hacia `Entrega/contractrisk-m3`. Sin permiso, solicitar acceso al propietario o usar un fork. No usar force-push ni fusionar a main sin revisión del equipo.

## Qué está hecho y qué NO

- Corpus: 24 fichas públicas SECOP II, no contratos completos; índice v5 de 133 chunks. Gold humano: 12 preguntas en `eval/gold_v1/eval_set.json`, todavía sin ejecutar como evaluación final.
- Cuatro variantes de desarrollo con Qwen2.5-3B-Instruct: sin recuperación, denso, avanzado híbrido/RRF/filtro ID/reranking y agente con herramienta de diferencia de valores.
- V5: 32/32 respuestas con formato válido; agente calcula dos diferencias correctamente. Esto NO significa 32/32 respuestas correctas. Hay tres llamadas innecesarias rechazadas, fallos de abstención y una auditoría inventada.
- Juez sin reemplazo automático de notas: 48 juicios reales sobre 12 pares sintéticos antes/después. Contradice evidencia numérica y confunde respuesta con fuente. La mitigación de verbosidad NO mejoró la medida.
- Pendientes grandes: harness final de tres dimensiones, métricas de dominio, RAGAS, comparación de las cuatro variantes sobre gold, informe final, declaración de IA y publicación revisada.
- La fila sin RAG usa un generador nuevo adaptado a QA: no atribuirla a RoBERTalex de M2. Confirmar rotulación con el profesor si es posible y declarar la adaptación.

## Próximo trabajo, en orden

1. Añadir pruebas de regresión basadas en v5: cifras sin respaldo, abstención contradictoria, auditoría inexistente en las fuentes y juez que evalúa la evidencia en lugar de la respuesta propuesta.
2. Probar ajustes acotados en desarrollo/calibración, preservando v5 intacta. No ajustar usando el gold final. No perseguir indefinidamente un resultado perfecto: documentar límites y decidir explícitamente la configuración que se congela.
3. Completar/versionar el harness común: métrica automática apropiada a QA, juez bruto y cumplimiento de dominio con criterios distintos. Definir fallos, faltantes, N/A y denominadores antes de medir.
4. Implementar las cuatro métricas RAGAS requeridas: faithfulness, answer relevancy, context precision y context recall. Seguir la guía/laboratorio; no renombrar métricas arbitrarias como RAGAS. Registrar evaluador, prompts, salidas y cobertura. Diferenciar implementación didáctica de librería oficial.
5. Congelar modelo/revisión, prompts, corpus, gold, métricas y dependencias. Ejecutar las mismas 12 preguntas en las cuatro variantes con mismo generador/prompt base y latencia mediana comparable. Guardar todos los resultados, incluidos fallos.
6. Escribir README/reporte con tablas, fuentes, límites, costos/tiempos, ejemplos y uso real de IA. Revisar con el equipo y luego abrir PR hacia main. Entrega en Interactiva la realiza el equipo, no se marca hecha sin comprobante.

## Mapa de código

| Archivo | Función |
|---|---|
| `run_integration_v5.py` | Corrida de desarrollo de cuatro variantes y calibración; NO harness final |
| `systems_v5.py`, `agent_v5.py` | Sistemas actuales y controlador acotado |
| `protocol_probe.py` | Prompts ANSWER_V5/ROUTER_V5 y generación compartida |
| `retrieval_advanced.py`, `rag_basic.py` | Recuperación avanzada, densa y carga del generador |
| `contract_tools.py` | Lectura de valores, cálculo Decimal, validación y fuentes |
| `judge.py`, `calibration_v1.py` | Juez, parser, 12 pares sintéticos y resumen |
| `tests/` | 62 pruebas locales en el estado auditado |
| `evidence/` | Diagnósticos y originales de las corridas anteriores |

## Pruebas y reproducción

Desde la raíz del repositorio, con Python:

```powershell
python -m unittest discover -s m3/tests -v
git diff --check
```

Las pruebas usan dobles sintéticos: pasar no acredita calidad de inferencia. Para reproducir v5 en Colab, generar el paquete desde la rama descargada:

```powershell
git archive --format=zip --output=contractrisk_m3_integracion_v5_codigo.zip HEAD m3
```

Abrir `m3/ContractRisk_M3_Integracion_v5_Calibracion_Colab.ipynb` en Colab, usar sesión nueva con GPU T4, subir ese ZIP en la primera celda y ejecutar en orden. Guardar notebook con salidas y ZIP de resultados. Este ZIP es transporte local: no agregarlo a Git (ya contiene evidencia versionada). No sobrescribir los resultados originales. La corrida v5 reproduce un diagnóstico, NO corrige por sí misma los fallos conocidos ni calcula RAGAS.

Las dependencias y revisiones están en los scripts/requisitos; Qwen 3B tiene licencia qwen-research, no asumir Apache. No subir pesos descargados ni claves. No cambiar versiones al azar: registrar cualquier cambio y volver a verificar compatibilidad.

## Reglas para una continuación honesta

- No modificar gold ni datos para mejorar resultados. No enviar referencias de corrección al sistema o indicadores de acierto al juez.
- No reemplazar notas del juez con 4/1 ni reintentar para conseguir una nota más alta. Reintentos de formato deben quedar registrados.
- No confundir una ficha sin auditoría con evidencia de que nunca hubo auditoría; no afirmar fraude/corrupción.
- Mantener historial de fallos; cada corrida nueva va en carpeta/version nueva. No inventar revisiones humanas ni métricas.
- Actualizar checklist con archivo/evidencia verificable y diferenciar implementado, ejecutado y validado. Consultar su sección vigente, no los pendientes históricos.
- Antes de cerrar: revisar secretos, rutas locales, licencias, reproducción, autoría y todos los requisitos de la guía. Main conserva la entrega anterior hasta aprobación explícita del merge.
