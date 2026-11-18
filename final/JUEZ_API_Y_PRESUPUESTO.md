# Ruta alternativa del juez — autorización y controles

18/11/2026: el usuario autoriza **USD 5 totales** para la API, manteniendo preferencia por gratuito. Sin recargas automáticas. [Política](api_budget_policy.json). **No se han realizado llamadas API ni activado cobros desde este trabajo.** La autorización no significa que el proveedor garantice ese techo.

## Candidato a preparar

Google AI Studio/Gemini es una alternativa a comprobar en la cuenta del usuario. La [documentación oficial de precios](https://aistudio.google.com/docs/pricing#gemini-3.8-flash), consultada el 18/11, presenta gemini-3.8-flash con nivel gratuito y, para Standard pagado hasta 31/12/2026, USD 0,75 por millón de tokens de entrada y USD 3,75 por millón de salida incluidos tokens de pensamiento. Disponibilidad, cuotas y precios se deben volver a verificar antes de ejecutar; no se ha fijado un candidato operativo ni demostrado que juzgue mejor. No usar modelos retirados o alias que redirijan silenciosamente.

Primero crear clave/proyecto de nivel gratuito, sin activar facturación. Guardar la clave únicamente como secreto de Colab, nunca en conversación o Git. Para calibración se enviarían anclas sintéticas ya aprobadas, no datos privados ni gold final. El [nivel gratuito puede utilizar contenido para mejorar productos](https://aistudio.google.com/docs/pricing); revisar condiciones antes de enviar datos distintos de los sintéticos.

## Si fuera necesario pagar

Proyecto dedicado, límite del proveedor/saldo compatible con USD 5 y recargas desactivadas. La [guía de facturación](https://aistudio.google.com/docs/billing) indica que puede solicitarse prepago mínimo de USD 5; si la cuenta exige más o los impuestos exceden la autorización, detenerse y consultar al usuario. Sus límites de gasto pueden tener retraso de aproximadamente diez minutos: no son una garantía instantánea.

Se preparó [api_budget.py](api_budget.py): registro persistente compartido entre corridas, reserva del coste máximo antes de cada petición, acceso serial con bloqueo y rechazo de nuevas reservas que excedan USD 5. Un timeout conserva su reserva; no se supone coste cero ni se reintenta automáticamente. Si el coste verificado supera la reserva, el registro se bloquea. Esto es una protección local **todavía no conectada a un transporte API**, no una garantía ante precios erróneos o uso externo de la cuenta.

Antes de cualquier llamada pagada faltan integración de precios actuales, conteo de tokens/razonamiento, límites de salida, SDK sin retries automáticos y prueba de que el registro no se reinicia en cada sesión. No añadir búsquedas, herramientas pagas, caché ni almacenamiento. Reservar inicialmente como máximo USD 1 del total para calibración; no gastar el resto sin auditar el resultado. No hace falta comprar un plan de chatbot para usar una API.

## Criterio académico

Otro proveedor no equivale a juez validado. Debe pasar calibración sintética conocida, prueba de verbosidad, confirmación nueva revisada y auditoría de motivos, con rangos/umbrales versionados antes de mirar sus notas. Las anteriores corridas fallidas se conservan. La puntuación de un modelo local nunca se renombra como puntuación de la API. El sistema contractual sigue ejecutándose en Colab/Space: la API, si se usa, será para evaluación offline, no una dependencia paga oculta de la demo.
