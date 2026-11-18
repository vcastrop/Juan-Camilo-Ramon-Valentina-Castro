# Hydrogen 09 — candidato nuevo, calibración pendiente

Estado 18/11/2026: cliente, runner y notebook preparados; pruebas locales simuladas, **sin llamadas reales a Hydrogen ni calidad aprobada**. [Notebook](ContractRisk_Final_Juez_09_Hydrogen_Colab.ipynb), [configuración](hydrogen_calibration_config.json), [presupuesto de fase](hydrogen_budget_policy.json). Main y Space intactos.

## Selección y API

El usuario mostró el catálogo donde figura gemini-4-hydrogen sin etiqueta Paid. La [ficha oficial](https://aistudio.google.com/docs/models/gemini-4-hydrogen) confirma texto y salidas estructuradas; la [guía de migración](https://aistudio.google.com/docs/whats-new-gemini-4-hydrogen) confirma GenerateContent y nivel gratuito. Esto no demuestra que la cuota de su proyecto permita inferir ni que un tercer intento en el mismo proveedor tenga disponibilidad.

Se fija ese modelo antes de obtener sus notas, sin fallback. Catálogo primero, conteo después; la primera ancla es la comprobación de generación real, sin ping generativo extra. Misma API key, proyecto gratuito confirmado, whitelist sin gold, rúbrica y umbrales anteriores. Otro modelo no equivale a mejor juez: debe pasar filtros y auditoría.

La guía desaconseja caps bajos de salida en Hydrogen. Se fija HIGH thinking y máximo explícito de **65.536 tokens combinados**, sin long decode, streaming, continuaciones, herramientas ni agentes. No se envían candidateCount ni parámetros de sampling ignorados. Se declara JSON Schema de puntaje entero 1–5 y razón breve. El catálogo puede anunciar salida de hasta un millón; la petición permanece limitada a 65.536. Se registra versión efectiva y debe permanecer igual dentro de la corrida; no es un hash de pesos inmutable. Modelo y presupuesto de generación cambian: no se atribuiría un delta a una única causa.

## Historia y contabilidad, sin reiniciar

Se preservó el ZIP 08 con hash fijo y se verifican su commit/fuentes, cero notas y snapshot de dos reservas de USD 0,3072. Antes de inferir, la misma carpeta de Drive debe conservar exactamente el registro y las dos marcas de 07/08. Si falta o cambió, se detiene; no reconstruir ni bajar reservas manualmente. El nuevo marcador hydrogen_calibration_candidate_1.started.json impide repetir desde otra sesión.

El techo total **sigue siendo USD 5**. Para el candidato nuevo se fija antes de observar notas un **sublímite acumulado de estimación de USD 2**, incluidas las reservas anteriores, en lugar del sublímite inicial de USD 1 aplicado a 07/08. La tarifa de referencia de Hydrogen es mayor: USD 1,50/M entrada y USD 7,50/M salida incluidos pensamientos, según [precios oficiales](https://aistudio.google.com/docs/pricing#gemini-4-hydrogen). El programa reserva usando ambos caps a la tarifa mayor. Una nueva petición sin uso verificable deja otra reserva de USD 0,6144: total histórico potencial USD 1,2288, no una factura.

No se habilita facturación. El titular debe confirmar Free Tier sin pago; el programa no verifica automáticamente ese estado. El registro local no garantiza impuestos, cambios tarifarios o uso externo: se mantiene modo gratuito declarado y revisión temporal de precios. La política inicial se conserva como historia; la política de fase y la configuración nuevas explicitan los USD 2, sin modificar el tope global.

## Calibración, sin sustituir notas

Se usan las mismas veinte anclas sintéticas aprobadas, piloto de nueve empezando por attribution_bad y agenda total de 38, sin mezclar notas históricas. Solo si pasa el piloto se completa la agenda. Exigencias: 38 válidas, al menos 18/20 en rango, cero malos principales con 4–5 y diferencias <=1 en cada par mitigado. Verbosidad evaluada realmente: sin normalización del texto en este candidato. Se conserva cada nota bruta, sin clamp, reintento semántico ni comparación gold enviada al juez.

Sin retries de transporte; un reintento máximo de formato si hay texto inválido, ninguno por truncamiento. Un error técnico detiene la agenda. El resumen distingue invalid_ids (sin nota válida), failed_ids (nota válida fuera de rango) y unexecuted_ids. Un 503 no se declara fallo semántico. Aunque pase, quedan confirmación nueva revisada y auditoría humana de motivos. Las anclas conocidas no se presentan como validación ciega.

## Ejecución

Runtime CPU; habilitar GEMINI_API_KEY y WANDB_API_KEY para notebook 09; conectar **la misma cuenta de Drive**. No subir ZIPs anteriores ni borrar marcas. Confirmar GRATUITO solo si se comprobó el proyecto sin facturación. Ejecutar en orden y descargar contractrisk_final_juez_hydrogen_resultados.zip y notebook con salidas incluso si se detiene. No activar pagos o cambiar modelos por ensayo y error.

182 pruebas final + 128 M3 aprobadas (310). Incluyen conservación de reservas, marcador único, cuerpos nativos acotados, catálogo unificado, exposición acumulada, parada sin retry, no fuga de gold, nota equivocada preservada y separación entre indisponibilidad y fallo semántico. No prueban API disponible, coste real ni juicio de Hydrogen.
