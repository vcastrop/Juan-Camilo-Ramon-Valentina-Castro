# Verificación de materiales de cierre

19/11/2026. Commit de contenido comprobado: `be103b3d19d3f3ac1db5457a61cf02dd6024feb1`.
Los ajustes posteriores de documentación no cambian los modelos ni los resultados.

## Copia limpia del repositorio

- Clon local completo, independiente (`--no-hardlinks`), de la rama de entrega.
- Historial auditado disponible; prepare_test_history conserva checkout.
- Recálculo de seis filas desde archivos versionados: JSON coincide con las
  tablas publicadas, OCR18/22, siete peticiones válidas y tres rechazos de entrada.
- Pruebas desde ese clon: **367 final + 128 M3 = 495, todas pasan**.
- Árbol del clon limpio tras ejecutar; sin modelos, GPU ni llamadas pagadas nuevas.
- Advertencias ResourceWarning de bucles asyncio no cerrados aparecen al finalizar
  pruebas de interfaz en Windows; no se presentan como errores de inferencia.

Se reutilizó un entorno Python existente: Python3.12.14, numpy2.5.5,
Pillow11.3.0, matplotlib3.10.6, W&B0.31.0, Gradio6.16.0. No fue una instalación
vacía de dependencias; la receta publicada fija numpy2.1.3 como las corridas
históricas. Esta comprobación no certifica reinstalación desde cero ni idéntico
comportamiento de modelos en otro hardware. No se reconstruyó aquí el índice
neural: se conserva evidencia de su construcción y uso en Colab/servicio.

## Documentos y presentación

- Enlaces locales de portada, reporte, reproducción, guion y matriz comprobados.
- Diez diapositivas renderizadas y revisadas visualmente; corregido desborde de
  texto en arquitectura. Tablas y diagrama editables en PowerPoint.
- Paquete PPTX y geometría: validadores sin hallazgos. Importación comprobada
  con el motor de generación, no apertura manual en Microsoft PowerPoint.
- SHA256 del PPTX final:
  `1ab86a2a8e7be51fcb8d345cbb9af2d0db61920a02186e29490e6b60c24840bf`.
- Búsqueda de patrones seleccionados de credenciales en texto versionado sin
  coincidencias. No equivale a auditoría exhaustiva de binarios, historial o
  archivos de todas las corridas públicas de W&B.

## Confirmación posterior del equipo

Juan Camilo y Valentina aprobaron los materiales finales. El equipo confirma
que realizó el ensayo y que la demostración salió satisfactoriamente. Esta
confirmación no añade otra corrida al benchmark ni una medición de duración.

## No se da por completado

Video de respaldo recomendado, coordinación de
sustentación y entrega en Interactiva con comprobante. La posterior
[integración autorizada en main](INTEGRACION_MAIN.md) está completada.
W&B conserva la incidencia Crashed sin causa confirmada. No se modifican sus
registros para aparentar continuidad. El servicio probado sigue siendo académico,
reducido y con cuatro fallos textuales conocidos; no está certificado para decisiones reales.
