# run.py – Ejecución del Pipeline RAG desde la Línea de Comandos

## Descripción General
El script run.py debe permitir la ejecución no interactiva del pipeline RAG mediante la línea de comandos, utilizando argumentos para especificar parámetros y adaptadores.

## Funcionalidades Requeridas
- **Parsing de Argumentos:**  
  - Utilizar librerías como argparse o click para capturar argumentos como: 
    - --input: Adaptador de carga de datos.
    - --input_path: Ruta o endpoint del origen de datos.
    - --embedder: Modelo de embeddings a utilizar.
    - --llm: Generador de respuestas.
    - --vector_store: Tipo de índice vectorial.
- **Inicialización del Pipeline:**  
  - Obtener la configuración global mediante core/config.py y actualizarla con los argumentos recibidos.
  - Inicializar RAGPipeline y ejecutar el flujo completo del procesamiento.
- **Salida en Consola:**  
  - Mostrar la respuesta generada o mensajes de error detallados en la terminal.
- **Consulta de Servicios Externos:**  
  - Antes de iniciar el pipeline, verificar mediante core/service_detector.py que todos los servicios externos requeridos están disponibles.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado por desarrolladores y administradores para pruebas o ejecuciones puntuales sin necesidad de una interfaz gráfica.
- **Interacción con Otros Módulos:**  
  - Se conecta directamente con pipeline.py, config.py y utils/logger.py para coordinar el proceso.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir su implementación personalizada.
- Incluir en el README ejemplos de comandos y salidas esperadas, así como manejo de errores.

## Conclusión
Este README proporciona la guía detallada para la implementación de run.py, asegurando que la ejecución del pipeline a través de la línea de comandos se realice de manera clara, robusta y extensible.
