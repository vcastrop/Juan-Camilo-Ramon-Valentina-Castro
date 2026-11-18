# Mistral — corrección de entrada y comparación controlada

Estado al 18/11/2026: corrección y evidencia CPU comprobadas; **no hay nueva inferencia ni mejora de juicio medida todavía**. [Notebook vigente](ContractRisk_Final_Juez_03_Tokenizacion_Colab.ipynb). No es un tercer modelo, ni se sustituyen las notas de [Mistral anterior](evidence/judge02_legacy/ANALISIS.md) o Qwen.

## Qué se encontró y qué sabemos

El método heredado `TrackedGenerator.generate` aplica la plantilla con `tokenize=False` y luego llama al tokenizer sin deshabilitar símbolos automáticos. [Transformers advierte](https://huggingface.co/docs/transformers/v4.57.0/chat_templating) que esto puede duplicar tokens y perjudicar el rendimiento: al tokenizar después debe usarse `add_special_tokens=False` o tokenizar directamente con la plantilla.

Diagnóstico real en Windows CPU con Transformers 4.57.6, tokenizers 0.22.2 y revisiones fijas, sin pesos ni GPU:

| Tokenizer | Mensajes con diferencia heredada frente a nativo | Mensajes corregidos iguales a nativo |
|---|---:|---:|
| Mistral v0.3 | 38/38 | 38/38 |
| Qwen2.5-7B | 0/38 | 38/38 |

Mistral comienza con IDs `[1,1,3,...]` en la ruta heredada y `[1,3,...]` en la nativa. En un ejemplo, 970 tokens frente a 969. Las longitudes heredadas reconstruidas coinciden con las registradas en los 38 intentos originales. No se guardaron los IDs completos en la corrida vieja: hablamos de reconstrucción y coincidencia de conteos, no de comparar un registro de IDs inexistente.

[Diagnóstico de ambos tokenizers](evidence/tokenization_cpu_01/diagnostic.json) y [preflight Mistral completo](evidence/tokenization_cpu_01/mistral_preflight.json). Confirman un defecto, no su efecto causal sobre las notas. El fallo Qwen no se explica por BOS duplicado según este diagnóstico. La correspondencia exacta de tokens tampoco garantiza comprensión de evidencia.

## Corrección acotada

- Se añade `NativeChatGenerator`, heredando **sin cambios el constructor/cargador** de `CausalGenerator`.
- Renderiza la misma conversación y tokeniza con `add_special_tokens=False`.
- Verifica en cada llamada igualdad completa de IDs con `apply_chat_template(tokenize=True)`. Ante discrepancia, falla; no genera sobre entrada no validada.
- Mantiene generación greedy, límite 320, EOS, checkpoint, NF4, FP16 y doble cuantización. Registra protocolo `native-chat-1`, longitud y huella de IDs; no envía contenido ni IDs a W&B.
- La clase heredada conserva su comportamiento para que las rutas históricas no se cambien silenciosamente; no se editó M3. Las corridas guardan commit y hashes para reproducir exactamente cada versión.

Se fija explícitamente tokenizers 0.22.2 en requisitos: es la versión que registra la instalación anterior, no una actualización elegida para lograr mejores notas.

## Antes de cargar el modelo en Colab

`tokenization_preflight.py` reconstruye los 38 mensajes con tokenizer real: debe igualar los conteos antiguos, reproducir un BOS extra y validar los 38 corregidos contra nativo. No descarga pesos ni usa GPU. Si no pasa, se conserva diagnóstico y no se carga el juez.

`run_mistral_tokenfix.py` exige el preflight fresco, su hash y fuentes sin cambios. Verifica archivo Mistral original, configuración canónica, rúbrica, anclas y criterios idénticos. El ejecutor compartido acepta una clase de generador inyectada, pero su ruta predeterminada sigue siendo la heredada; solo el wrapper nuevo selecciona `NativeChatGenerator` y registra la comparación.

GPU y versiones registradas de torch/transformers/accelerate/bitsandbytes/W&B deben coincidir con el perfil anterior. Si cambian, se detiene sin cargar el modelo; no se fuerza una rebaja de paquetes manual. Son sesiones Colab distintas con el mismo perfil, no certificación de misma tarjeta física ni driver (no se registró toda esa información antes). No es benchmark de eficiencia.

## Qué se medirá y qué no cambia

Los mismos 38 juicios con rúbrica 1.1: 38 válidos, al menos 18/20 dentro de rango, ningún malo con 4–5, seis pares mitigados con diferencia máxima 1. Notas brutas intactas; reintento únicamente por formato. Comparar las razones además de los promedios y no relajar umbrales por el plazo.

Si pasa, todavía **judge_validated_for_final=false**: faltan revisión/ejecución de doce anclas separadas ya preparadas y auditoría de razones. Si falla, no repetir para seleccionar notas favorables ni afirmar mejora por haber arreglado la entrada.

## Comprobaciones locales

100 pruebas final CPU + 128 M3 aprobadas. Incluyen prueba con tokenizer simulado, rechazo de tokens distintos al nativo, constructor/generación sin cambio de parámetros, preflight de todos los casos y conservación del camino antiguo. El diagnóstico real de tokenizers es evidencia distinta de esos tests. No hay ejecución de pesos Mistral corregida en el equipo local.

## Ejecución del equipo

Sesión nueva T4, secreto `WANDB_API_KEY` accesible para este notebook, celdas en orden. Se descargan ZIP y notebook con salidas. El ZIP incluye preflight, metadata, juicios y logs incluso si falla la carga. No modificar main ni Space con este candidato todavía.
