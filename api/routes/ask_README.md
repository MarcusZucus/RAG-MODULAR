# ask.py – Endpoint /ask para Consultas del Usuario

## Descripción General
El módulo ask.py debe definir el endpoint /ask que permita recibir un prompt del usuario, procesarlo a través del pipeline RAG y retornar una respuesta estructurada.

## Funcionalidades Requeridas
- **Validación de Entrada:**  
  - Utilizar modelos Pydantic para validar y sanitizar la consulta del usuario.
- **Invocación del Pipeline:**  
  - Llamar a RAGPipeline (ubicado en core/pipeline.py) para procesar la consulta y generar la respuesta.
- **Estructuración de la Respuesta:**  
  - Retornar un JSON que incluya la respuesta, metadatos (como tiempos de procesamiento, métricas) y logs relevantes.
- **Manejo de Errores y Seguridad:**  
  - Implementar mecanismos de rate limiting y autenticación, y gestionar errores mediante excepciones HTTP.
- **Referencia a Servicios Externos:**  
  - Antes de procesar la consulta, se debe validar que los servicios externos requeridos estén disponibles consultando core/service_detector.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Es el principal punto de interacción para que los usuarios obtengan respuestas generadas por el sistema RAG.
- **Relación con Otros Módulos:**  
  - Se conecta directamente con pipeline.py y utiliza core/config.py para obtener parámetros de configuración.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir que se complete la implementación posteriormente.
- Incluir en el README ejemplos de solicitudes y respuestas esperadas, y describir casos de manejo de errores.

## Conclusión
Este README es la guía esencial para la implementación del endpoint /ask, asegurando que la comunicación entre el usuario y el sistema RAG sea robusta, segura y eficiente.
