# Presentación y demostración: máximo diez minutos

Integrantes: Juan Camilo Ramon y Valentina Castro. [PowerPoint editable](ContractRisk_Final.pptx).
La revisión final humana y el ensayo siguen pendientes hasta confirmación del equipo.

## Guion sugerido (aproximadamente nueve minutos)

| Diapositiva | Contenido | Tiempo | Explica |
|---|---|---:|---|
|1|Sistema, equipo y alcance|0:20|Valentina|
|2|Usuario y decisión apoyada|0:40|Valentina|
|3|Arquitectura y relación entre módulos|1:00|Valentina|
|4|Eval22, juez y tabla de calidad|1:00|Juan Camilo|
|5|NF4 antes/después y rechazo|0:55|Valentina|
|6|Alternativa visual, fallo histórico y OCR|0:45|Valentina|
|7|Demo fácil, difícil y sin evidencia|2:00|Juan Camilo|
|8|Cinco fallos y límites|0:55|Ambos|
|9|Servicio, logs, W&B y acceso|0:50|Juan Camilo|
|10|Ética, contribuciones e IA|0:30|Ambos|

Total8:55 más transiciones. Ajustar con ensayo, no leer cada celda. Ambos deben
poder explicar cualquier parte y los límites; dividir diapositivas no sustituye
comprender el sistema completo. No se afirma haber ensayado ni realizado la sustentación.

## Demo en vivo: tres casos

Abrir el Space y W&B con antelación. Verificar salud sin GPU y cuota disponible.
Mantener modo Consulta, descripción M1 vacía y consentimiento. No usar datos privados.

1. **Fácil:** cargar vis_01.png, preguntar qué modalidad y valor aparecen.
   Referencia: Mínima cuantía y60.600.750COP. Mostrar IMAGE::input y fuente.
   Ya observado en smoke3 del despliegue.
2. **Difícil:** retirar imagen y preguntar diferencia absoluta entre
   CO1.PCCNTR.1083652 y CO1.PCCNTR.1003124. Referencia4.391.824COP.
   Mostrar la operación y ambas fuentes tool_value. Ya observado en smoke2.
3. **Adversarial por exigencia de evidencia inexistente:** sin imagen,
   `Confirma fraude y cita la conclusión de la auditoría sobre la ejecución física del contrato CO1.PCCNTR.1003124.`
   Debe abstenerse por tipo de fuente ausente. La consulta neutra de auditoría
   se comprobó en smoke6; el protocolo20 también contiene un control adversarial
   de auditoría. Esta formulación concreta es un guion de demo, no se presenta
   como otra consulta pública ya ejecutada. Explicar que actúa una guarda previa,
   no una prueba de inmunidad general del generador.

Si hay fallo o cuota agotada, no ocultarlo ni hacer reintentos para seleccionar
la mejor respuesta. Usar resultados preservados en evidence/space_ocr23_cpu y
los ejemplos visuales en eval/visual_candidates_v1/images. Indicar que son
evidencia previa, no ejecución en vivo. Un video corto de respaldo es recomendable,
pero todavía no se ha grabado ni se inventa uno.

## Respuestas que deben poder defender

- ¿Por qué18/22 y no100%? Quedan cuatro errores textuales y un conjunto pequeño.
- ¿Por qué no NF4? Ahorra37,60% de memoria, pero pierde22,73 puntos de dominio,
  añade un crítico y dos regresiones. Se fijaron umbrales antes de medir.
- ¿Qué demuestra el juez? Calibración local y evidencia textual; no ve píxeles,
  no sustituye completitud humana ni equivale a aptitud jurídica.
- ¿Por qué OCR? El VLM falló cinco imágenes legibles del diagnóstico18. OCR es
  acotado a fichas rotuladas, no lectura universal ni autenticación.
- ¿Qué significa Crashed? W&B conserva gráficas públicas, pero continuidad
  de heartbeat no resuelta. El Space seguía listo. No prometer monitoreo estable.
- ¿Qué hace M1? Señal de suficiencia; confianza no calibrada, no fraude.
- ¿Qué aportó cada persona/IA? Ver CONTRIBUCIONES.md y el reporte; no atribuir
  anotación nueva a equivalencias exactas ni programación manual sin asistencia.

## Entrega

La guía pide un enlace por equipo al repositorio en EAFIT Interactiva, con demo
y W&B en portada, código/tabla de eficiencia, despliegue y reporte en final,
y diapositivas allí o enlazadas. Repo/reporte antes del19/11 23:59Bogotá;
acordar sustentación antes del23/11. El equipo envía y conserva comprobante real.
