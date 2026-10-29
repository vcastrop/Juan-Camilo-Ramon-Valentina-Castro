# Ruta única de lectura y reproducción — M3

## Versión de referencia

La entrega consolidada toma como base el bundle del compañero `bc93baa`, integrado con las auditorías y pruebas locales. No sustituye main. El informe es [README.md](README.md) y la lista operativa es [CHECKLIST.md](CHECKLIST.md).

| Etapa | Código que produjo la evidencia | Evidencia de referencia | Estado |
|---|---|---|---|
| Generación, harness y RAGAS originales | `6026ac4`; `run_final_m3.py`, `harness_m3.py`, `ragas_m3.py` | [final_m3](results/final_m3/ANALISIS.md) | Ejecutada, histórica 1.0 |
| Recálculo determinista | `1575907`; `harness_m3_v11.py`, `rescore_m3.py` | [Tabla harness 1.1](results/final_m3_rescore_v1_1/tablas_m3_v1_1.md) | Referencia vigente del harness |
| Reevaluación RAGAS sin regenerar respuestas | `1575907`; `ragas_m3_v11.py`, `rerun_ragas_m3.py` | [Tabla RAGAS 1.1](results/final_m3_ragas_v1_1/tablas_ragas_v1_1.md), [auditoría](results/final_m3_ragas_v1_1/ANALISIS.md) | Referencia vigente de RAGAS |

Harness: `m3-harness-1.1`. RAGAS: `m3-ragas-lab-1.1`. Las notas del juez del harness siguen siendo las de la corrida original; la reevaluación RAGAS no reemplaza ese juez.

## Qué abrir o ejecutar

1. Para revisar sin GPU: leer las tablas y el detalle original por caso. El corpus y gold están congelados.
2. Para reproducir la generación y evaluación original en T4: [notebook final](ContractRisk_M3_Final_Colab.ipynb). Produce métricas 1.0, no el recálculo 1.1 automáticamente.
3. Para obtener harness 1.1 desde respuestas guardadas, desde la raíz del repositorio:

   ```bash
   python m3/rescore_m3.py m3/results/final_m3 m3/results/reproduccion_harness_v11
   ```

   La carpeta de salida debe ser nueva. El script conserva respuestas y notas del juez.
4. Para reproducir RAGAS 1.1: [notebook RAGAS 1.1](ContractRisk_M3_RAGAS_v1_1_Colab.ipynb). En su primera celda, usar `USE_ZIP = False` cuando la rama consolidada esté publicada; el modo ZIP necesita un paquete de código, no un ZIP de resultados. Alternativamente, en entorno T4 con dependencias instaladas:

   ```bash
   python -u m3/rerun_ragas_m3.py --run m3/results/final_m3 --output m3/results/reproduccion_ragas_v11
   ```

5. Pruebas sin inferencia:

   ```bash
   python -m unittest discover -s m3/tests -v
   ```

Para reconstruir exactamente el código de una ejecución registrada, usar su commit de la tabla en un clon separado. Los notebooks por defecto pueden clonar la rama móvil; registrar siempre el commit obtenido. No prometer identidad numérica entre entornos distintos solo por fijar la semilla.

## Candidatos y auditorías que NO generan las tablas vigentes

Se conservan en sus rutas para no romper imports, pruebas ni referencias históricas; están separados por este registro, no eliminados.

- `audit_rules_m3.py`, `rescore_audit_m3.py` y [audit_m3_1_1](results/audit_m3_1_1/RESUMEN.md): auditoría paralela de Codex, versión `m3-harness-audit-1.1`. Coincide en los dos cambios de dominio, pero NO es `m3-harness-1.1` del reporte y no define sus columnas de recuperación.
- `ragas_audit_m3.py`, `run_ragas_audit_m3.py`, `package_audit_m3.py`, `ContractRisk_M3_Auditoria_Colab.ipynb`: candidato alternativo `m3-ragas-audit-1.1`, probado localmente, SIN corrida GPU. No confundir con RAGAS 1.1 del compañero ya ejecutado.
- `harness_qa.py`, `ragas_course.py`, [HARNESS_QA.md](HARNESS_QA.md) y [RAGAS_METODO.md](RAGAS_METODO.md): núcleos candidatos, no tablas finales.
- [Corrección v6](evidence/correction_v6/ANALISIS.md): diagnóstico de desarrollo no adoptado completo por regresiones. V1–v5 y sus notebooks son antecedentes.
- [CIERRE_AUDITADO.md](CIERRE_AUDITADO.md): plan anterior a recibir RAGAS 1.1. Sus solicitudes de corrida no son pendientes vigentes.

## Límites que esta consolidación no resuelve

No modifica generador, métricas, prompts ni notas. Persisten errores del juez y de abstención. Los ajustes de redacción y controles pendientes se listan en CHECKLIST.md. El análisis documental original fue corregido por el compañero; las respuestas, métricas originales y logs no se modificaron. No describir toda la carpeta como byte a byte intacta si su ANALISIS.md recibió una fe de erratas.
