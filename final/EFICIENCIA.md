# Eficiencia — reglas aprobadas antes de comparar

El usuario aprobó en conversación los umbrales el 16/11/2026 Bogotá. Registro UTC 17/11/2026 04:10:28. [Política versionada](efficiency_policy.json). No se ha ejecutado una comparación FP16/NF4 ni se ha aceptado cuantización. La corrida visual 03 es perfilado previo de desarrollo, no el antes de la comparación definitiva.

## Condiciones de aceptación conjunta

1. Caída máxima de **5 puntos porcentuales absolutos** en tasa de cumplimiento del dominio bajo un harness común, no cinco por ciento relativo. Por ejemplo, 80 % a 75 % cumple el límite; 80 % a 74 % no. No se sustituirá esta métrica por el proxy literal de visual 03.
2. **Cero fallos críticos nuevos**: se compara por caso y tipo, no solo cantidad agregada. Corregir un error en un caso no permite introducirlo en otro.
3. **Cero regresiones** de controles de abstención, adversariales e invarianza por caso/par. No compensarlas con mejor promedio.
4. **Al menos 20 % menos memoria CUDA pico asignada**: máximo de `torch.cuda.max_memory_allocated()` de los mismos casos, en bytes, con todos los componentes GPU residentes. No mezclar peso del archivo, memoria reservada ni memoria total del dispositivo con esta magnitud. Reservada y latencia p50/p95 se informan aparte.

Se aceptan los bordes exactos: caída de 5 puntos y ahorro de 20 %. La implementación compara fracciones, sin tolerancias de coma flotante que cambien el criterio. Aceptar eficiencia relativa no certifica calidad absoluta de la base ni aptitud para decidir contratos.

## Técnica candidata, no resultado

Cuantización **NF4 de 4 bits en los pesos del mismo generador Qwen2.5-3B**, cálculo FP16; VLM, corpus, recuperación, prompts, parser, control de consistencia 0.3 y parámetros de generación iguales en ambos lados. No cambiar simultáneamente de modelo, prompt o recuperación para atribuir su efecto a la cuantización. La doble cuantización y cualquier parámetro adicional deben fijarse al cerrar configuración, antes de ejecutar.

La API de `BitsAndBytesConfig` y la cuantización NF4 están documentadas en [Transformers](https://huggingface.co/docs/transformers/v4.57.0/quantization/bitsandbytes). La [guía de instalación de bitsandbytes](https://huggingface.co/docs/bitsandbytes/en/installation) documenta soporte por arquitectura/CUDA, y [PyPI](https://pypi.org/project/bitsandbytes/0.50.2/) publica 0.50.2 con rueda Linux x86-64. Referencias consultadas 16/11/2026 Bogotá. Son respaldo de viabilidad, **no prueba de compatibilidad real con nuestra combinación de Colab ni con ZeroGPU**. La dependencia y sus hashes se fijarán en el entorno de la prueba; no se ha instalado ni ejecutado todavía.

Cuantizar no garantiza menor latencia. Se conservarán resultados negativos, fallos de carga y regresiones; no se cambiará el umbral después para que el candidato pase. No desplegarlo hasta medir y auditar compatibilidad del Space.

## Preparación de decisión automática

`efficiency_acceptance.assess(before, after)` devuelve:

- `not_evaluable`: faltan datos, no hay calibración del juez aprobada, cambia hardware/casos/harness/configuración compartida, falta alguna categoría de control o no se verificó que el generador usa cuantización. No es aceptación implícita.
- `rejected`: evidencia comparable pero incumple al menos uno de los cuatro criterios.
- `accepted_relative_efficiency`: cumple todos los criterios; no equivale a aprobación del producto para uso real.

Cada perfil requiere una fila por caso: ID, `domain_pass` booleano, tipos de fallo crítico, controles pertinentes booleanos, pico CUDA asignado y latencia. IDs/controles deben coincidir; desconocidos, duplicados o datos inválidos impiden aceptación. Los hashes comunes identifican gold, harness, configuración del juez, prueba de calibración, configuración de inferencia compartida y esta política. La huella de política usa JSON canónico, independiente de finales de línea Windows/Linux. Los reportes deben ser producidos por el futuro ejecutor medido y auditados contra sus registros, no escritos a mano.

Las pruebas actuales usan **datos sintéticos de unidad**, no resultados de cuantización. Comprueban límites, pérdida absoluta frente a relativa, hardware/casos distintos, falta de calibración, controles omitidos y fallos ocultos por promedios. Total actual: 66 pruebas final CPU y 128 heredadas M3 aprobadas.

## Trabajo siguiente antes de gastar GPU en comparación

1. Cerrar conjunto común textual/visual y tratamiento explícito de entradas visuales por sistemas sin visión; conservar que el gold anterior ya se inspeccionó.
2. Versionar tres dimensiones distintas y definir fallos críticos/controles por caso, sin restaurar notas forzadas ni llamar accuracy a cobertura de hechos.
3. Preparar calibración del juez con evidencia sintética separada, incluyendo cifras con cero adicional, explicación incorrecta, abstención injustificada, contradicción entre fuentes y respuestas breves. Fijar aceptación antes de ejecutar; si falla, no usarlo para aprobar la pérdida de calidad.
4. Congelar hashes, implementar y comprobar carga NF4 real; medir antes/después en la misma T4 y con la misma versión de consistencia 0.3. La carga/calentamiento y las solicitudes se separan; pares y muestra pequeña se declaran al interpretar percentiles.
5. Aplicar esta política y auditar respuestas/errores. Decidir qué se publica, sin modificar resultados originales.

Por tanto, los umbrales están aprobados, pero **el protocolo común, el juez calibrado y la medición de eficiencia siguen pendientes**. No se pide repetir visual 03 para obtener un puntaje mayor.
