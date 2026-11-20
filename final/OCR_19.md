# Candidato OCR 19 — comprobación CPU previa a integración

La [corrida 18](evidence/visual18_completed/ANALISIS.md) rechaza utilidad visual
del lector Qwen en esas cinco imágenes legibles. Se conserva la implementación
histórica y todo su resultado. No se cambia el Space ni el scorecard del final.

## Decisión técnica acotada

Probar **un candidato distinto**, Tesseract 5, en lugar de seguir muestreando el
mismo Qwen. Dos segmentaciones fijas (3/6), idiomas spa+eng y motor LSTM. La
salida TSV conserva texto y confianza por palabra, según la
[documentación oficial](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html).
No hay corpus, respuestas esperadas o consultas al juez en el lector.

Campos críticos deben concordar entre segmentaciones. Se rechazan identificador
ausente, campos ambiguos y confianza mínima inferior a 80 en palabras del campo.
Ese 80 es un umbral operativo fijado antes de medir, **no 80 % de probabilidad de
acierto**. Dos segmentaciones del mismo motor tienen errores correlacionados:
no se presentan como dos verificadores independientes ni garantizan corrección.
No reparar O/0, l/1, completar IDs ni elegir cifras mirando el snapshot/gold.
Si ambas lecturas omiten el valor, permanece ausente: no se inventa.

## Protocolo congelado

Doce imágenes: las ocho anteriores, intactas, y cuatro nuevas sintéticas
(importe sin/con separadores, ID ausente y dos valores contradictorios). Ocho
casos tienen campos completos y cuatro son parciales/controles. Los dos nuevos
importes pertenecen a una pareja de la misma ficha ficticia, no dos ejemplos
independientes. Son pruebas de desarrollo, post-hoc y pequeñas.

**El valor alterado es una prueba de lectura:** extraer 251000000 de una imagen
que lo imprime puede ser correcto como OCR, pero no valida el dato contractual
frente al snapshot de 250000000. La concordancia con fuentes y la generación QA
no se ejecutan en 19. Un OCR exacto no demuestra un sistema integrado correcto.

## Ejecutar sin GPU ni claves

1. Abrir `ContractRisk_Final_OCR_19_Colab.ipynb`.
2. Seleccionar hardware **Ninguno / CPU**. No hace falta T4.
3. Ejecutar en orden. Se instala Tesseract en el entorno temporal de Colab;
   no en el equipo personal. Se registran versión/idiomas y hashes de datos
   de idioma cuando su ruta es accesible; APT no se presenta como lockfile.
4. Enviar ZIP y notebook con salidas. Si falla, usar la última celda para el parcial.

Una sola tanda, sin búsqueda de parámetros o reintentos. El umbral y modos no se
ajustan después para mejorar la cifra. No requiere facturación, Gemini, W&B ni
descargar pesos Qwen. Las pruebas locales usan TSV simulados; **el motor real no
se ha ejecutado localmente** porque no está instalado. Resultado CPU pendiente.

Regresión local: 330 pruebas final + 128 M3 aprobadas (458). Nueve prueban el
nuevo protocolo/lector con TSV simulados, incluidos ceros extra, confianza baja,
ID ausente, ambigüedad y separación entre extracción y verdad de la fuente.
El rechazo de TSV vacío se comprobó además en ese bloque después de la suite.
No confundir estas pruebas con una ejecución del motor OCR real.

## Después

Si aporta utilidad, integrar como nueva versión con controles de fuente/abstención
y evaluar los casos afectados, comparando con el original. Conservar el VLM
como línea base; no atribuirle las mejoras OCR ni reutilizar su scorecard como
si describiera esta nueva ruta. Revisar requisitos académicos y licencias antes
de elegir el despliegue definitivo. Si falla, documentar el límite y decidir
alcance; no iniciar búsqueda abierta de lectores. Verificación pública, reporte,
roles/IA y presentación siguen pendientes.
