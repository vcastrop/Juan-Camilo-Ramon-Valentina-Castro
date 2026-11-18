# Continuación 06 — fallo de juicio confirmado

Auditoría 18/11/2026. Código `2f763eed5abe691fe3034669b52e5d110908fad8`. [Integridad](audit.json): 16 hashes de fuente verificados, notebook con mismo contenido fuente y sin errores de celdas, siete registros previos idénticos, mismo perfil de paquetes y Tesla T4. Resumen recalculado idéntico. Logs: 130 pruebas final + 128 M3.

Se reutilizaron siete juicios y se ejecutó **uno nuevo**: attribution_bad. No hubo reintento de formato ni truncamiento. Carga real NF4 de 252 Linear4bit, sin offload. El modelo dio **4** cuando el rango aprobado era 1–2. Su propia razón reconoce que el número se atribuye incorrectamente al objeto en vez del valor. Sus soportes literales son reales, pero no justifican una nota alta para esa explicación falsa.

El evaluador 1.1 conservó el 4 y marcó high_score_despite_reported_defect. Se detuvo deliberadamente: ocho juicios totales, accusation_good no ejecutado y ninguna regresión completa ni prueba nueva de verbosidad. No es otro fallo de la regla anterior de fragmentos diagnósticos: es una contradicción semántica del juez entre defecto reconocido y nota concedida.

Estado original completed_pilot_failed. Juez rechazado para aceptación de calidad/eficiencia. No se bajan umbrales, no se transforma el 4 en 2 y no se selecciona otra ejecución. Los originales permanecen intactos. W&B krzcgzx8 finalizó según logs; acceso al dashboard no verificado.

Ruta posterior: preparar candidato de API con calibración previa, presupuesto total autorizado de USD 5 y preferencia por nivel gratuito; no hay llamadas ni calidad aprobada de ese candidato todavía. En paralelo se prepara el harness común sin convertir notas experimentales en cumplimiento validado.
