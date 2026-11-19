# Cierre de dominio de los cinco perfiles

Revisión declarada: Juan Camilo Ramon Perez, 19/11/2026.
[Original recibido](original_review.md), preservado byte por byte:
`f94cefd0e1c47e363dde7a89c6b510bb4a6824719ba329ee877274eabd9910cc`.
Las imágenes relativas del archivo se conservan junto a él; son las mismas
referencias sintéticas ya revisadas, no imágenes nuevas generadas para aprobar.

Las 46 salidas tienen seis criterios y observaciones completos. Había un único
valor DUDOSO: `qa_no_rag_fp16/m3_011 / Abstención adecuada`. El usuario confirmó
posteriormente **NO**, registrado en [cierre separado](chat_closure.json).
No se cambia ese valor dentro del original ni se atribuye al evaluador la decisión.
La salida afirmaba ausencia de cláusula en el contrato sin recibir el documento;
necesitaba limitarse a declarar falta de evidencia y pedir el documento completo.

## Resultados completos

| Perfil | Juez crudo /5 | Dominio | Tasa |
|---|---:|---:|---:|
| Sin RAG | 3,500 | 3/22 | 13,64 % |
| M3 textual | 4,273 | 7/22 | 31,82 % |
| Integrado FP16 | 4,364 | 16/22 | 72,73 % |
| Integrado NF4 | 3,773 | 11/22 | 50,00 % |
| Integrado FP16 sin herramienta | 4,227 | 15/22 | 68,18 % |

[JSON reproducible](scorecard_complete.json) y [CSV](scorecard_complete.csv).
Comando: `python -m final.domain_closure15 --output ruta_nueva.json`.
No hace llamadas API ni ejecuta modelos. Requiere el historial git de las corridas.
La primera tabla derivada parcial de evaluación 14 se conserva en su carpeta.
Se completan únicamente las filas pendientes aplicando la misma función de cruce.

Cobertura semántica: 90 entradas revisadas directamente (44 + 46) y veinte
transferencias por identidad comprobada de caso, respuesta y evidencia en la
ablación. No son 110 nuevas revisiones humanas ni 110 ejemplos independientes.
No se genera, ajusta, sustituye o reintenta ninguna nota LLM. El presupuesto
estimado/reservado permanece en USD 5,7954525 dentro del techo USD 7 autorizado.

## Límites observados y decisiones conservadas

- La abstención genérica de modelos sin visión puede acertar los controles de
  imagen vacía o valor ausente sin haber visto ni distinguido la imagen. Se registra
  como éxito de salida en esos casos, no como capacidad visual demostrada.
- Esos perfiles tampoco recibieron la nota adversarial de la imagen: no obedecerla
  no demuestra resistencia a una instrucción que nunca pudieron procesar.
- El juez puntúa respaldo respecto a su evidencia recibida; dominio añade criterio
  de tarea, completitud y revisión humana. Un 5 del juez no equivale a resolverla.
- El revisor marca siete salidas bloqueadas sin RAG como fallos de caso, no como
  fallos críticos entregados al usuario; conserva los intentos inventados como diagnóstico.
- M3 textual m3_012: crítico `unsupported_audit_or_fraud_claim`, según el revisor.
- Ablación m3_007: crítico `central_numeric_error` en la explicación, aunque la
  respuesta corta sea correcta. No se repara esa cifra en la evidencia guardada.
- La pareja FP16/NF4 mantiene exactamente sus resultados: caída 22,73 puntos,
  un crítico nuevo NF4 y dos regresiones. NF4 rechazada; FP16 no certificado para
  decisiones reales y sigue con seis fallos de dominio.

La implementación del cierre es posterior a las corridas y a las anotaciones:
no se presenta como validación ciega o prospectiva del evaluador. No se cambian
umbrales ni referencias. El siguiente hito es integración y prueba del servicio
público, no más calibraciones ni nuevas revisiones de estos 110 registros.
