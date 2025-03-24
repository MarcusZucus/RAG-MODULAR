# embedding_model.py – Interfaz para Modelos de Embeddings

## Descripción General
Define el contrato para adaptadores que convierten textos en vectores numéricos, fundamental para el proceso de indexación y búsqueda en RAG.

## Funcionalidades Requeridas
- **Método embed(texts: List[str]):**  
  - Recibir una lista de textos y retornar sus representaciones vectoriales en un formato estándar.
  - Soportar procesamiento en lote y manejo de errores internos.
- **Optimización y Cache:**  
  - Considerar la integración con utils/cache_manager.py para almacenar y recuperar resultados previamente calculados.
- **Consulta de Servicios:**  
  - Antes de invocar servicios externos de embeddings, consultar core/service_detector.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Implementado en adaptadores de embeddings, por ejemplo, openai_embedder.py y sentence_transformer_embedder.py.
- **Interacción:**  
  - Los vectores generados se utilizarán en el pipeline para la búsqueda semántica.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para permitir una implementación personalizada.
- Documentar en el código ejemplos de entrada y salida esperados para facilitar pruebas unitarias.

## Conclusión
Este README es la guía esencial para la implementación de embedding_model.py, asegurando que cualquier adaptador de embeddings se integre perfectamente en el sistema RAG.
