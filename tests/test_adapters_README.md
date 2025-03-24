# test_adapters.py – Pruebas Unitarias para Adaptadores

## Descripción General
El archivo test_adapters.py debe contener pruebas unitarias específicas para cada adaptador, verificando tanto su funcionamiento en condiciones normales como el manejo adecuado de errores.

## Funcionalidades Requeridas
- **Pruebas de Inputs:**  
  - Validar el funcionamiento de adaptadores de carga de datos (por ejemplo, json_loader, sql_loader, api_loader).
- **Pruebas de Embeddings:**  
  - Evaluar que los adaptadores de embeddings (por ejemplo, openai_embedder, sentence_transformer_embedder) generen vectores en el formato esperado.
- **Pruebas de Vector Stores:**  
  - Verificar que los adaptadores de vector stores (por ejemplo, faiss_store, chroma_store) manejen correctamente la inserción y búsqueda de documentos.
- **Pruebas de LLMs:**  
  - Probar que los adaptadores de generación de respuestas (por ejemplo, openai_generator, local_llm_generator) devuelvan resultados coherentes y manejen errores apropiadamente.
- **Registro y Reporte:**  
  - Cada prueba debe documentar resultados y registrar incidencias para facilitar la depuración.
- **Verificación de Servicios Externos:**  
  - Incluir pruebas para confirmar que los adaptadores consultan core/service_detector.py antes de utilizar servicios externos.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado para garantizar que cada adaptador cumple con su contrato y se integra correctamente en el pipeline.
- **Relación con Otros Módulos:**  
  - Se conecta con las interfaces definidas en core/interfaces/ y utiliza utilidades como utils/logger.py para el registro.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir la implementación de pruebas detalladas.
- Incluir en el README ejemplos de escenarios de prueba y formatos de salida esperados.

## Conclusión
Este README es la guía para implementar test_adapters.py, asegurando que cada adaptador del sistema RAG funcione de manera independiente y en conjunto de forma robusta.
