# Salud disponible tras corrección CPU — recibida del usuario

El usuario aportó JSON y dos capturas del botón de salud, versión
5b42adc35d6e3225c93dfbda13ae2e1730bad1c8. Declara:

- statusalive, contract_system_readytrue, startup_errornull.
- generator/classifier/embedding/rerankertrue; index_readytrue.
- visual_reader_readytrue, Tesseract5.5.0, spa/eng con hashes idénticos a la
  referencia OCR19/20; evaluated_language_data_matchtrue.
- vlm_loadedfalse, cuatro modelos esperados, real_request_verifiedfalse.
- W&B not_tested.

Esto respalda que la inicialización del backend terminó en HF. No prueba una
petición GPU, una predicción M1, lectura OCR correcta en esta versión ni W&B.
No se confunde health con evaluación o disponibilidad de cuota. Tesseract5.5.0
difiere de5.3.4 en Colab aunque coincidan los archivos de idioma: registrar el
entorno y comprobar las imágenes en vivo. El 18/22 sigue siendo de Colab.

Fuente: JSON/capturas enviados por el usuario, no una comprobación independiente
desde sesión externa. El intento de abrir la API pública de metadatos con la
herramienta web no devolvió contenido accesible; no se marca acceso externo.

Siguiente: siete rutas de smoke de DESPLIEGUE_OCR_22, conservar resultado y evento
de cada una, salud tras la primera consulta y run W&B con acceso externo probado.
No reinstalar, no repetir Colab21 ni editar secretos para esta etapa.
