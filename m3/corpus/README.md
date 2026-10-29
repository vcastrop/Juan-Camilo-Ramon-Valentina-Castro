# Corpus candidato: fichas públicas SECOP II

Estado: descargado y validado técnicamente; pendiente de revisión humana y congelación para evaluación.

## Fuente y transformación

- Fuente: [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h).
- Entidad atribuida en el catálogo: Agencia Nacional de Contratación Pública - Colombia Compra Eficiente, Bogotá D.C.
- Identificador del conjunto: `jbjy-vk9h`.
- Licencia declarada por los metadatos consultados: Creative Commons Attribution Share Alike 4.0 International, `CC_40_BY_SA`. [Condiciones enlazadas por la fuente](https://creativecommons.org/licenses/by-sa/4.0/legalcode).
- La captura, consultas exactas y metadatos de licencia están en `source_snapshot.json`. Los datos derivados se mantienen bajo la licencia de su fuente, con atribución y esta declaración de transformación; ello no licencia los materiales privados del curso.
- Transformación: selección de campos públicos necesarios y representación determinista como líneas «campo: valor». No se generan narrativas ni se completan campos faltantes con un modelo.
- Se excluyen de la selección números de identificación personal, cuentas bancarias, nombres de representantes y supervisores. Las descripciones públicas originales se conservan; falta revisión humana antes de publicar para detectar datos personales innecesarios dentro del texto libre.

## Composición

24 fichas: cuatro de obra, cuatro de suministros, cuatro de compraventa, cuatro de consultoría, cuatro de arrendamiento de inmuebles y cuatro de prestación de servicios. Entre 70 y 186 palabras por ficha serializada. No son 24 contratos completos ni 24 PDFs.

Selección intencional, no aleatoria ni representativa: primeros registros utilizables por ID dentro de cada tipo y del filtro `fecha_de_firma` en 2024. Se consultaron hasta 80 candidatos por tipo. Se excluyen IDs y descripciones exactamente iguales tras normalizar espacios y mayúsculas respecto de train/validation M1 y gold M2. Resultado: cero coincidencias bajo esas comprobaciones; esto no demuestra ausencia de toda similitud semántica.

## Archivos

- `source_snapshot.json`: captura seleccionada, fecha UTC, consultas, procedencia y licencia.
- `documents.jsonl`: documento por ficha, identificador, texto y enlaces citables. Este es el insumo de indexación, sin etiquetas gold.
- `manifest.json`: cantidad, tipos, comprobación de intersección y SHA-256.
- `../prepare_corpus.py`: descarga o reconstrucción offline; rechaza sobrescribir una captura existente.

Desde la raíz del repositorio:

```bash
python m3/prepare_corpus.py --snapshot m3/corpus/source_snapshot.json --output-dir /tmp/contractrisk-m3-rebuild
python -m unittest discover -s m3/tests -v
```

La carpeta de salida debe ser nueva o estar vacía. Una descarga nueva desde la API puede diferir porque la fuente cambia; para replicar la evaluación se usa el snapshot congelado, no una recaptura silenciosa.

## Calidad y límites

En `CO1.PCCNTR.1088236`, la fuente registra firma en 2024 e inicio/fin en 2019. En `CO1.PCCNTR.1109703` sucede una discrepancia similar. Se preservan estos valores; no sabemos por qué aparecen así. Las preguntas temporales deberán distinguir «dato registrado» de «hecho comprobado» y señalar inconsistencias cuando proceda.

«No Definido», campos vacíos y una duración que solo indica «Dia(s)» no proporcionan un dato completo. No permiten inventar ciudad, duración ni fechas corregidas. Los valores son los registrados, sin ajuste por inflación ni verificación de pago real.

El corpus sirve para consultar objetos, entidades y campos de fichas y estudiar recuperación/citas/abstención. No contiene por sí mismo actas, cláusulas completas, ejecución física ni hallazgos de auditoría. No permite confirmar corrupción, incumplimientos o sobrecostos. Una pregunta que requiera esa evidencia debe producir abstención o indicar qué documentación falta.

## Verificación inicial

Se ejecutaron cuatro pruebas unitarias y una reconstrucción offline. Los SHA-256 del snapshot y documentos reconstruidos coinciden con los del manifiesto. Esto comprueba la preparación de datos, no el funcionamiento del RAG: todavía no se ha construido el índice ni ejecutado el modelo de M3.
