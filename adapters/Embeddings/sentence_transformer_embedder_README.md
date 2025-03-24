# sentence_transformer_embedder.py – Adaptador para Generación de Embeddings con Modelos Locales

## Descripción General
El módulo debe implementar la generación de embeddings utilizando modelos locales (por ejemplo, de HuggingFace) para entornos sin conexión.

## Funcionalidades Requeridas
- **Carga de Modelo Local:**  
  - Cargar el modelo y el tokenizador de HuggingFace, gestionando la selección de dispositivo (CPU/GPU).
- **Procesamiento en Batches:**  
  - Dividir textos en lotes (batches) para optimizar la inferencia y reducir el tiempo de respuesta.
- **Cálculo de Embeddings:**  
  - Procesar los textos y extraer los vectores representativos, normalizando la salida para integrarla en el pipeline.
- **Registro de Operaciones:**  
  - Documentar cada operación de inferencia y gestionar excepciones a través de utils/logger.py.
- **Consulta de Servicios Externos:**  
  - Aunque se use un modelo local, se recomienda consultar core/service_detector.py para conocer el entorno y recursos disponibles.

## Integración con el Sistema
- **Uso Principal:**  
  - Se invoca cuando la opción de embeddings locales es seleccionada en la configuración.
- **Interfaz:**  
  - Debe adherirse al contrato definido en core/interfaces/embedding_model.py.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir una implementación basada en estas directrices.
- Documentar internamente ejemplos de salida y posibles optimizaciones de recursos.

## Conclusión
Este README es la guía para implementar sentence_transformer_embedder.py de forma que ofrezca una alternativa robusta y escalable a la generación de embeddings a través de modelos locales.
