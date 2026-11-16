# Corrección 02 — lectura visual y elegibilidad de herramienta

Estado: código y regresiones CPU comprobados; nueva inferencia T4 pendiente. No sustituye el Space actual ni aprueba la entrega final.

## Cambios y motivo

1. El VLM transcribe únicamente `legible` y `texto_visible`. Un parser separado reconoce campos por etiquetas visibles y conserva los literales usados. No recibe corpus, gold ni valores esperados. Campos ausentes, ambiguos o formatos no reconocidos permanecen null; no se reconstruyen IDs incompletos.
2. Una imagen con rango de luminancia máximo de dos niveles se bloquea como uniforme antes de inferencia. Es un control determinista muy limitado: no mide legibilidad general, no detecta toda imagen vacía o borrosa y puede rechazar señales extremadamente débiles. Sus resultados no se atribuyen al VLM.
3. Si la pregunta visual pide modalidad, valor u objeto y falta el campo leído, la aplicación se abstiene en vez de rellenarlo desde el snapshot.
4. Solo se habilita el router/herramienta de diferencias cuando la pregunta incluye exactamente dos IDs distintos y solicita diferencia de valores. Para otras consultas se responde con el generador y RAG sin pasar por el router. Es un patrón de agente acotado por política; no es una prueba de que el LLM aprendió a enrutar mejor.
5. Registro de excepciones, esquema válido, abstención y uso del VLM separados. Ni esquema válido ni ausencia de excepciones equivalen a respuesta correcta.

Las reglas se desarrollaron después de inspeccionar resultados de integración 01. Se declaran correcciones post-hoc, no evaluación ciega. No se editaron resultados originales ni se renombró una salida antigua como nueva inferencia.

## Prueba enfocada

[Notebook de corrección 02](ContractRisk_Final_Correccion_02_Colab.ipynb). Sesión nueva T4, secreto W&B habilitado si se desea registro remoto. Se copian las cuatro imágenes originales del ZIP conservado, verificando hashes. No hace falta subir imágenes ni paquetes adicionales.

Primero se prueba el VLM, después se libera y se carga una sola vez el generador para consultas y orquestación desde lecturas guardadas. No se repite M1, que ya cargó en el ensayo anterior. Esto reduce trabajo redundante, pero sigue sin medir latencia visual fresca de punta a punta ni carga conjunta de producción.

El ZIP nuevo conserva replay CPU identificado como post-hoc, lecturas nuevas del VLM, respuestas finales, trazas, errores, metadata y origen de imágenes. W&B finaliza en finally y no recibe contenido de preguntas ni imágenes.

## Criterios de revisión de desarrollo (no son la rúbrica final)

- Las fichas legibles producen campos respaldados por su transcripción; comparar además contra las imágenes, no solo contra el esquema.
- La imagen uniforme se bloquea por control de píxeles, sin atribuir su rechazo al modelo.
- La consulta de modalidad no intenta herramientas.
- La diferencia conserva operación y ambos operandos.
- Fuentes ausentes continúan produciendo abstención.
- La respuesta final y sus citas responden a la pregunta; una transcripción correcta sola no basta.

El siguiente hito, tras revisar esta corrida, es preparar el conjunto visual humano de al menos cinco casos y la ejecución multimodal real de producción, antes de congelar protocolo y medir eficiencia.
