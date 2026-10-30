# Desarrollo v3: ejecución completa, calidad aún insuficiente

Corrida T4 del 29/10/2026, 05:38–05:43 UTC (00:38–00:43 Colombia). Originales conservados: [ZIP](contractrisk_m3_desarrollo_v3_resultados.zip) y [notebook ejecutado](ContractRisk_M3_Desarrollo_v3_Agente_Colab_Ejecutado.ipynb). No se alteraron salidas ni se evaluó el gold final.

## Verificación técnica

Metadata completed; 32 registros (cuatro variantes, ocho preguntas); 42 pruebas locales aprobadas en Colab; sin outputs de tipo error en el notebook. Hashes de código coinciden con el paquete v3 entregado. Los 133 chunks y todos los contextos, incluidos los campos de herramienta, coinciden con offsets del corpus. Esto acredita ejecución y procedencia, no calidad de respuesta.

| Variante | Salidas válidas de esquema | Mediana por consulta, segundos |
|---|---:|---:|
| Control sin RAG | 5/8 | 2.071 |
| Denso | 4/8 | 4.119 |
| Avanzado | 6/8 | 4.705 |
| Agente | 3/8 | 11.202 |

Total 18/32 válidas. Una salida válida aún puede ser incorrecta. Los errores de validación se guardan por diseño sin detener la corrida: completed no equivale a todos los casos correctos. No son métricas finales ni resultados de juez/RAGAS.

## Fallos constatados

1. Avanzado sigue respondiendo Compraventa (tipo) en lugar de Contratación directa (modalidad) para CO1.PCCNTR.3156756, pese a tener ambos campos en c003.
2. Avanzado inventa que una auditoría de CO1.PCCNTR.1637043 concluyó ejecución correcta. Las fichas no contienen ese informe; estado, valor y duración no lo prueban. La respuesta tiene JSON y citas válidos, pero carece de sustento.
3. El controlador solicita diferencia de valores en cinco preguntas que no la necesitan, repitiendo el mismo ID como ambos operandos. La herramienta rechaza correctamente esos argumentos; las llamadas duplicadas quedan bloqueadas.
4. En dos cálculos, el controlador primero usa action=diferencia_valores_contratos con arguments, en vez del esquema action=tool/name/arguments. Las dos primeras decisiones son rechazadas; la tercera ejecuta correctamente la herramienta. Es una variante de formato inequívoca que puede normalizarse en una versión futura sin inventar la decisión ni los argumentos, conservando el original.
5. Resultados correctos de herramienta: abs(77000000 - 1766080) = 75233920 COP; abs(4500000 - 231096000) = 226596000 COP. Ambos comprobados contra campos fuente. Ninguno termina en una respuesta válida: el generador copia objetos enteros de evidencia en citas, y el texto termina en mitad del JSON. Los finales son compatibles con agotamiento del límite de generación de 320 tokens; no se registró finish_reason para demostrarlo directamente.
6. En el segundo cálculo, el texto generado dice 22,659,600 COP en vez de 226596000 COP: además del formato, hay un error numérico. No se debe corregir silenciosamente ni contarlo como acierto.
7. El caso sin llamada (auditoría) termina por agotamiento de pasos y no por una decisión answer válida. No cumple todavía la demostración de selección correcta de no usar herramienta.

## Próxima corrección controlada (pendiente)

- Reducir el paquete visible al generador a identificadores/textos y resultados compactos; conservar metadatos completos fuera del prompt. Evitar duplicar objetos de fuentes dentro del resultado de herramienta.
- Normalizar únicamente variantes inequívocas observadas del controlador, con pruebas sobre estas trazas; nunca transformar prosa ambigua en una llamada ni completar IDs.
- Reforzar controlador con ejemplos sintéticos separados del gold de llamada/no llamada; mantener límite de pasos y bloqueo de repetición. No forzar decisiones según etiquetas esperadas.
- Definir esquema visible de citas como lista de strings; añadir registro de tokens/terminación y, si procede, un reintento de formato común y acotado para todas las variantes. Preservar primer intento y error.
- Reforzar distinción entre campos y ausencia de auditoría/clausulado. Comprobar en desarrollo, no afirmar que escribir una instrucción soluciona el fallo.
- Repetir esta prueba antes del gold; si persisten errores, valorar un generador alternativo bajo las mismas condiciones para todas las filas, declarando el cambio y sus costos.

El juez independiente puede calibrarse en paralelo al desarrollo, pero no debe usarse para maquillar estos errores. Las notas de M3 siguen pendientes, así como RAGAS y la comparación final. Main permanece fuera de estos cambios.
