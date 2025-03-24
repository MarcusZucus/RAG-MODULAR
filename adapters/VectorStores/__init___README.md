# __init__.py (VectorStores) – Registro e Inicialización de Adaptadores de Índices

## Descripción General
Este archivo centraliza el registro de todos los adaptadores de vector store disponibles en el proyecto RAG.

## Funcionalidades Requeridas
- **Registro Centralizado:**  
  - Importar y registrar adaptadores como faiss_store.py y chroma_store.py.
- **Interfaz Unificada:**  
  - Proveer una API que permita al sistema seleccionar dinámicamente el adaptador correcto basado en la configuración.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado por loader.py para inyectar dinámicamente el vector store adecuado.
- **Extensibilidad:**  
  - Facilitar la incorporación de nuevos adaptadores sin modificar la lógica central.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para permitir su futura implementación.
- Documentar en el README ejemplos de registro y mecanismos de selección.

## Conclusión
Este README es la guía para implementar el archivo __init__.py en la carpeta VectorStores, asegurando un registro organizado y escalable de los adaptadores de índices.
