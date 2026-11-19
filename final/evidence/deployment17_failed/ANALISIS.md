# Recepción 17 — entorno preparado, auditoría bloqueada por historial incompleto

Se conservan ZIP, notebook ejecutado y captura originales sin modificar.

- ZIP SHA256: `f3068f801b75ee732a171b7d0c35292b3f2b8b8286b0408de5d791aa31547174`.
- Notebook SHA256: `5768028161511621632041f962cc134e46eace0193d70a7976ff2c601a0f3a5e`.
- Checkout: `bad47c801c6a00b7a805feb18790f5fa12a18725`.

## Lo que sí ocurrió

Instalación terminó; `deployment17_environment.json` indica todos los paquetes
del proyecto fijados, sin ausentes/desajustes/conflictos entre ellos. Gradio
6.16.0 y Hub 0.36.2. Torch observado 2.14.1+cu130 y GPU Tesla T4. Fuentes
DejaVu instaladas. Las advertencias de pip sobre otros paquetes preinstalados
(diffusers, tweepy, google-adk) siguen en el log: la comprobación de entorno se
limita al software del servicio, no certifica todos los paquetes de Colab.

## Primer fallo real

`deployment17_tests_final.log`: 227 pruebas ejecutadas y 23 errores. Algunos
`setUpClass` impidieron ejecutar todos sus métodos; no son 227/310 aprobadas.
Los 23 errores corresponden a `git show <commit histórico>:<archivo>` con código
128. Las auditorías requieren cuatro revisiones anteriores. El notebook clonaba
con `--depth 1`, omitiendo esos objetos. Es un defecto de preparación del
notebook, no de instalación, API, GPU o nuevas respuestas del modelo.

El bloqueo de preparación se mantuvo en falso (`setup_state.json`) y detuvo
la celda siguiente antes del empaquetado/inferencia. No hay nuevos resultados
contractuales ni cargos API. Tampoco se ejecutó la suite M3 en esta corrida,
pues la celda se detuvo en la suite final.

## Corrección y comprobación

El notebook 17 vigente clona la rama con historial completo y ejecuta
`prepare_test_history.py` antes de las pruebas. El ayudante completa clones
superficiales y comprueba las cuatro revisiones, sin checkout/pull/reset,
sin modificar archivos ni cambiar HEAD. No se desactivan pruebas de auditoría.

Se creó una copia local limpia del mismo commit con historial completo:
310 pruebas final + 128 M3 aprobaron. Además se reprodujo un clon superficial
real y se restauró su historial con el ayudante: HEAD permaneció en `bad47c8`,
las cuatro revisiones quedaron disponibles y se eliminó el estado superficial.
Tres pruebas nuevas verifican restauración, ausencia de descargas innecesarias
y configuración de historial del notebook. No se cargaron modelos CUDA aquí.

No se altera código del servicio, prompts, pesos, datos ni evaluación anterior.
La sesión T4 actual puede reutilizarse: completar historial, repetir celda de
preparación y continuar solo si termina. Para sesiones nuevas usar notebook 17
actualizado. Inferencia T4, despliegue ZeroGPU y verificación pública pendientes.
