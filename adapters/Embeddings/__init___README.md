# __init__.py (Embeddings) – Registro e Inicialización de Adaptadores de Embeddings

## Descripción General
Este archivo debe centralizar y documentar todos los adaptadores de generación de embeddings disponibles, facilitando la selección dinámica a través de metadatos.

## Funcionalidades Requeridas
- **Registro de Adaptadores:**  
  - Incluir la importación de adaptadores como openai_embedder.py y sentence_transformer_embedder.py.
- **Interfaz Unificada:**  
  - Proveer una API que permita seleccionar el adaptador correcto basado en la configuración del sistema.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado por loader.py para inyectar dinámicamente el adaptador de embeddings.
- **Extensibilidad:**  
  - Permitir la incorporación de nuevos adaptadores sin modificar la lógica central.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para que el desarrollador lo complete conforme a estas directrices.
- Incluir comentarios en el futuro que expliquen la lógica de registro y selección.

## Conclusión
Este README detalla la estructura y requerimientos para la correcta implementación del archivo __init__.py en la carpeta de Embeddings, asegurando una integración modular y escalable.
