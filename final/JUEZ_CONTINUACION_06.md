# Continuación 06 — evaluador literal 1.1

Estado 18/11: recálculo CPU terminado, continuación GPU preparada y no ejecutada. [Notebook](ContractRisk_Final_Juez_06_Continuacion_Colab.ipynb), [configuración](judge_continuation_config.json), [corrida 05 y diagnóstico](evidence/literal_05/ANALISIS.md).

## Qué cambia

Solo la validación de soportes del juez: una fuente disponible no citada por la respuesta puede demostrar un defecto cuando el juez declara contradicción, incompletitud o insuficiencia y marca citas sin respaldo. No puede utilizarse como respaldo de una respuesta declarada sustentada. Fuente desconocida, cita inventada o no contigua y campo ausente continúan rechazados. No se transforma la fuente diagnóstica en una cita de la respuesta.

La corrección es post-hoc y versionada. Las instrucciones antiguas imponían una restricción excesiva; se conservan en esta continuación para no cambiar las entradas del modelo ni repetir siete inferencias. Por ello no se afirma que la salida 05 siguiera todas las instrucciones antiguas: se reinterpreta explícitamente con el evaluador corregido. Una futura versión de prompt deberá armonizar esa instrucción y calibrarse por separado; no se cambiará silenciosamente durante esta continuación.

Se mantienen modelo/revisión, NF4/FP16, muestreo, semilla por caso, normalización literal, agenda y umbrales numéricos. No hay ajuste de nota ni reintento semántico. 19/20 o cualquier otro buen promedio no permite ocultar un falso positivo crítico.

## Reutilizar sin seleccionar

El ZIP 05 original tiene hash fijado. El cargador comprueba su configuración, commit y 15 hashes de fuente contra Git y contra la inferencia vigente. Carga exactamente los siete registros consecutivos ya ejecutados. Conserva notas, razones, verificaciones, soportes y salidas originales; guarda las alertas históricas por separado y recalcula las nuevas. No toma notas de otros candidatos.

Primero se ejecutan attribution_bad y accusation_good. Si falla alguno, se detiene. Si pasan, se realizan los otros 29 juicios: **31 nuevos en total** y siete reutilizados para completar 38, más como máximo un reintento de formato por juicio. Se informa procedencia y número realmente ejecutado; no se presenta como una única sesión nueva de 38. W&B registra solo las nuevas inferencias.

El entorno debe coincidir con el original: Tesla T4 y las mismas versiones efectivas de torch, transformers, tokenizers, bitsandbytes y W&B. Si cambia, se detiene antes de descargar pesos para decidir una comparación válida, no se relaja la comprobación. Igualdad de perfil no garantiza identidad universal de resultados entre sesiones.

## Qué aún no demuestra

El recálculo de siete no valida al juez, no prueba verbosidad y no resuelve las imprecisiones semánticas observadas. La confirmación separada de doce casos requiere revisión humana antes de ejecutarse. Una regresión aprobada tampoco reemplaza auditoría de razones ni autoriza a llamar ciego al conjunto conocido.

Si vuelve a fallar, conservar las notas y revisar el límite antes de crear otro candidato: no repetir para elegir resultados ni bajar umbrales. La entrega aún necesita harness común, comparación eficiente, ablación, aplicación pública real, W&B de consultas y reporte/presentación. El trabajo del juez no sustituye esos objetivos.

## Ejecución del equipo

Abrir el notebook 06 en una sesión nueva Colab T4; habilitar acceso a WANDB_API_KEY; ejecutar en orden. El ZIP anterior ya está preservado en el repositorio, no hace falta subirlo manualmente. Descargar el ZIP nuevo y notebook con salidas también si se detiene. No cambia main ni Space.

130 pruebas final y 128 M3 aprobadas localmente. Prueban el recálculo, rechazo de citas inventadas/fuentes desconocidas, imposibilidad de usar una fuente no citada como respaldo positivo, conservación de notas, prompt idéntico y agenda sin regenerar los siete casos. No prueban buen juicio de las inferencias pendientes.
