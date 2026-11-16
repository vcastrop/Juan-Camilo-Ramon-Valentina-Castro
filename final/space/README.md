---
title: ContractRisk Colombia
emoji: 🔎
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.32.0
python_version: "3.12"
app_file: app.py
pinned: false
short_description: Consulta contractual con fuentes y revisión humana
---

# ContractRisk Colombia — comprobación inicial de infraestructura

Esta versión comprueba interfaz, endpoint de salud, registro sanitizado, conexión opcional con W&B y asignación de GPU. **No responde consultas contractuales ni procesa imágenes todavía.** Los modelos y el índice no están integrados; `/readyz` responde 503 expresamente.

No introducir datos personales. Los botones generan eventos técnicos sin preguntas, imágenes, OCR ni valores introducidos por el visitante.

- `GET /healthz`: proceso vivo, sin asignar GPU ni ejecutar inferencia.
- `GET /readyz`: disponibilidad del sistema contractual; no listo en esta versión.
- Botón **Registrar prueba técnica**: un evento real de infraestructura, no una respuesta de ContractRisk.
- Botón **Probar asignación GPU**: operación de tensor pequeña, consume cuota ZeroGPU, no carga modelos.

Configuración opcional en Settings del Space:

- Secret `WANDB_API_KEY`: clave del titular, nunca en archivos.
- Variables `WANDB_ENTITY=jcramonp-eanit`, `WANDB_PROJECT=contractrisk-final`.
- Variable `CONTRACTRISK_VERSION`: commit de GitHub del paquete publicado.

Sin clave, los eventos siguen saliendo en JSON por stdout y W&B figura desactivado. La ausencia de clave no se considera observabilidad W&B cumplida. El reporte remoto registra eventos identificados como `infrastructure_smoke`, separados de las futuras consultas reales.

Los errores del proveedor no se muestran completos ni se registran credenciales. Las cuotas, tiempos de espera y políticas de retención de los proveedores aplican. Los secretos de Colab no se transfieren al Space.
