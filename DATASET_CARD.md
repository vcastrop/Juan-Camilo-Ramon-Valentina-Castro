# Dataset Card — ContractRisk M1

## Resumen

Dataset supervisado de 699 descripciones contractuales en español procedentes de SECOP II. La tarea consiste en clasificar suficiencia descriptiva, no legalidad ni riesgo de corrupción.

## Fuente

- Productor: Agencia Nacional de Contratación Pública - Colombia Compra Eficiente.
- Portal: https://www.datos.gov.co/d/jbjy-vk9h
- Recurso: SECOP II - Contratos Electrónicos.
- Campos consultados: `id_contrato`, `descripcion_del_proceso`, `tipo_de_contrato`.
- Consulta limitada a 100.000 registros mediante API Socrata.
- Idioma: español.
- Cobertura: Colombia.

Fuente: Portal de Datos Abiertos www.datos.gov.co. Los derivados se distribuyen siguiendo las condiciones de atribución y compartir igual aplicables al portal (CC BY-SA 4.0).

## Etiquetas

- `REQUIERE_REVISION` / `0`: el texto no permite comprender claramente el objeto sin información adicional.
- `SUFICIENTE` / `1`: el objeto principal se comprende razonablemente.
- `DESCARTAR`: decisión de anotación para ausencia de texto analizable; se excluye del dataset binario.

## Protocolo

- Guía humana con reglas, ejemplos y casos frontera.
- Calibración de 15 casos.
- Piloto de 50 casos con Kappa 1.000.
- Ampliación de 650 casos, con 100 compartidos.
- Control ampliado: acuerdo 87 %, Cohen's Kappa 0.683.
- Trece desacuerdos adjudicados y documentados.
- No se utilizó `tipo_de_contrato` para decidir etiquetas.

## Estadísticas

| Clase | Total |
|---|---:|
| SUFICIENTE | 544 |
| REQUIERE_REVISION | 155 |

Split estratificado reproducible con semilla 42: 559 train y 140 validation. No existe solapamiento por ID ni texto.

## Limitaciones

- Desbalance de clases: 22,2 % requiere revisión.
- Muestreo enriquecido por tipos y posibles casos difíciles; no representa la prevalencia natural completa.
- La suficiencia descriptiva admite juicios frontera.
- Puede haber textos truncados, fórmulas repetitivas y errores ortográficos provenientes de la fuente.
- No debe emplearse para acusar fraude, corrupción o ilegalidad.
