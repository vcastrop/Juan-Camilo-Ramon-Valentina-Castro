# API 08 — recuperación única tras HTTP 503

Actualización de ejecución: [08 también recibió 503 sin notas](evidence/api_08/ANALISIS.md). No repetirlo. Se preparó [Hydrogen 09 como candidato nuevo](JUEZ_HYDROGEN_09.md), conservando ambos intentos y sus reservas. El texto siguiente documenta la preparación original, no una recuperación exitosa.

Estado 18/11/2026: código, notebook y simulación local preparados; **sin reintento real ejecutado**. [Notebook](ContractRisk_Final_Juez_08_API_Reintento_Colab.ipynb), [evidencia original 07](evidence/api_07/ANALISIS.md). No se modifica main ni Space.

## Motivo y alcance

La corrida 07 intentó una generación y recibió 503, sin texto final ni nota. Después de explicar la indisponibilidad y proponer un único reintento controlado, el usuario pidió continuar. No se repite para elegir una nota favorable: no existe una nota anterior. La [guía oficial](https://aistudio.google.com/docs/troubleshooting#retry-strategy) considera 503 UNAVAILABLE un error transitorio susceptible de reintento limitado; el estado HTTP solo no identifica su causa concreta.

Se mantienen archivos originales del cliente, configuración, modelo, prompt, rúbrica, semillas por ancla, JSON Schema, agenda de 38 y umbrales. Se añade un runner de recuperación y controles de procedencia, no un nuevo protocolo semántico. No hay fallback de modelo, cambio de plan, retries automáticos de transporte o generación de varias notas para elegir. El único reintento de formato del protocolo original se mantiene si se devuelve texto inválido; no aplica a un 503.

## Controles previos

api_503_recovery.py verifica hash exacto del ZIP, commit original y diez fuentes contra Git y las fuentes vigentes, configuración y la ausencia de respuesta/puntuación previa. El notebook descarga el commit 71912f1 para esa comprobación y 6ec8dcd para pruebas históricas. No necesita subir el ZIP manualmente.

Requiere la misma carpeta `/MyDrive/ContractRisk_final_budget/` con api_budget_ledger.json y gemini_calibration_candidate_1.started.json. El registro debe coincidir con el snapshot de la corrida 07, manteniendo su reserva de USD 0,3072. Si falta o cambió, se detiene antes de inferir: **no reconstruir, borrar, liberar reservas ni reiniciar a mano**.

Se crea exclusivamente gemini_calibration_candidate_1_503_recovery.started.json. Su existencia bloquea otra recuperación, incluso desde otra sesión. El catálogo del modelo debe conservar sus metadatos previos (sin depender del orden de métodos); de lo contrario, se detiene antes de generar.

## Presupuesto y resultados

No se habilita modo pagado. El titular debe volver a confirmar que su proyecto es Free Tier sin facturación. La reserva original se conserva y una nueva petición reserva su propio máximo estimado. Si vuelve a producirse 503, ambas reservas suman USD 0,6144; no son dos cargos confirmados. Ambas cuentan en el **mismo** sublímite de estimación de calibración de USD 1 y techo total autorizado de USD 5. Los registros no comprueban una factura ni cubren cambios de precios/uso externo; sigue vigente la revisión de precios del protocolo original.

Si el servicio vuelve a responder, se evalúa primero attribution_bad y luego el resto del piloto. Solo si pasan los nueve completa la agenda de 38. Las notas del intento 07 sin respuesta no se mezclan con nuevas puntuaciones ni se contabilizan como juicios válidos. Metadata distingue la petición HTTP histórica de las nuevas. Aunque supere regresión, faltan auditoría humana y confirmación nueva previamente revisada; no se declara validado el juez.

Si vuelve a fallar un API call, se detiene y conserva parciales, sin nuevos retries. Un error 403/404/429/503 o formato sin nota no es mala puntuación de casos pendientes. No se promete disponibilidad del servicio por haber pasado pruebas de código.

## Ejecución

1. Abrir notebook 08 en Colab; basta CPU.
2. Habilitar GEMINI_API_KEY y WANDB_API_KEY para este notebook, sin pegar valores.
3. Ejecutar en orden y montar **la misma cuenta de Drive** usada en 07.
4. Escribir GRATUITO únicamente si se verificó el proyecto sin facturación.
5. Descargar contractrisk_final_juez_api_reintento_resultados.zip y el notebook con salidas incluso si se detiene.

173 pruebas final y 128 M3 aprobadas localmente (301). Incluyen ausencia de nota previa, rechazo de archivo alterado, contabilidad/marker ausentes o modificados, conservación de reserva, presupuesto acumulado, body de inferencia idéntico, cambio de catálogo y simulación del runner con un único 503 nuevo. No se hicieron llamadas reales al servicio desde este entorno.
