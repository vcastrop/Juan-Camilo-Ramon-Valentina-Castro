# Segundo juez — Mistral, regresión controlada y confirmación separada

Estado: preparado y comprobado en CPU; **no ejecutado en T4**. El [primer juez falló](evidence/judge_calibration_01/ANALISIS.md) y no se acepta ni se cambian sus notas. El objetivo aquí es mejorar y comprobar el juicio, no solo obtener JSON válido.

## Candidato y cambio controlado

[`judge_second_config.json`](judge_second_config.json): `mistralai/Mistral-7B-Instruct-v0.3`, revisión `c170c708c41dac9275d15a8fff4eca08d52bab71`, NF4, cálculo FP16, doble cuantización, semilla 42, máximo 320 tokens. Otra familia que Qwen; no garantía de mejor juicio ni prueba de independencia estadística respecto a los datos.

Modelo/revisión/licencia pública Apache-2.0 verificados en [metadata oficial](https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.3). La [ficha oficial](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) incluye uso con Transformers y mensajes system/user; se comprobó también la [plantilla del tokenizer en la revisión fija](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/raw/c170c708c41dac9275d15a8fff4eca08d52bab71/tokenizer_config.json). Consultado 17/11/2026. La compatibilidad del paquete en nuestra T4 sigue necesitando ejecución real; no se prometen notas ni memoria.

No se cambian rúbrica 1.1, anclas aprobadas, formato, criterio de aceptación, parámetros compartidos, parser ni política de reintento. `verify_second_config` rechaza cambios de esos parámetros para no atribuir su efecto al checkpoint. La regla de explicación vacía máxima 2 sigue como instrucción al modelo, nunca como edición de score.

## Paso A: regresión en lo conocido

[Notebook Mistral](ContractRisk_Final_Juez_02_Mistral_Colab.ipynb), sesión T4 nueva y acceso a `WANDB_API_KEY`. No necesita nuevos archivos/revisiones para este paso: usa las veinte anclas ya aprobadas y los seis pares, 38 juicios con el mismo filtro:

- 38/38 juicios válidos después de como máximo un reintento de formato.
- Al menos 18/20 dentro de rango, sin ningún caso malo en 4–5.
- Seis pares mitigados válidos, diferencia máxima de un punto en cada par.

Si falla: conservar la corrida y no declarar al modelo apto. No cambiar de modelo/versiones en la celda ni repetir hasta escoger mejores notas.

Si pasa: status `completed_regression_passed_confirmation_pending`; **judge_validated_for_final permanece false**. Los ejemplos se inspeccionaron tras el fallo Qwen y ahora se usan en selección de candidato: llamarlo regresión de desarrollo, no confirmación independiente.

## Paso B: confirmación nueva, preparada pero no ejecutada

`eval/confirmation_v1/` fija doce respuestas ficticias sobre campo/tipo de dato, monto con separadores, fuentes contradictorias, explicación vacía, cita de fragmento y auditoría inferida desde un estado. Entradas/rangos no proceden del gold final. Se prepararon después de diagnosticar Qwen pero **antes de inferir Mistral**; son ejemplos dirigidos de confirmación, no muestra aleatoria ni completamente ciega.

Revisión humana pendiente de pregunta, fuentes, respuesta, razón y rango. No existe aprobación ficticia. El notebook A no lee ni ejecuta ese paquete. Si A pasa, se solicitará esa revisión y se preparará B con los hashes ya fijados; no se reescribirán ejemplos para favorecer las nuevas respuestas.

Criterios B fijados antes de medir: 12/12 juicios válidos, al menos 11/12 dentro de rango (>=90 %), ningún ejemplo malo en 4–5. Las reglas de sesgo del paso A permanecen, no se reducen a una media. Aunque A+B pasen, hay que revisar las razones reales y falsas atribuciones de evidencia; las notas correctas con razones inventadas no prueban buen juicio.

## Evidencia y límites

Guardar salidas originales, configuración y versiones; W&B solo recibe metadatos técnicos/latencia sin pregunta, fuentes ni respuesta. Kernel NF4 antes de cargar checkpoint; detección de capas 4bit reales y rechazo de offload. Fallos se conservan y no generan puntuaciones inventadas.

93 pruebas final CPU + 128 heredadas M3 aprobadas, incluyendo conservación del fallo Qwen, configuración controlada, separación de confirmación y fallos de gates. Usan resultados guardados o dobles sintéticos: no equivalen a inferencia Mistral ni validación de calidad.

La eficiencia y el scorecard común no se aprueban mediante un juez no validado. Si también falla este candidato, se documentará y se decidirá explícitamente un evaluador más capaz o un rediseño validado, sin afirmar que todo quedó correcto ni ocultar el coste/plazo.
