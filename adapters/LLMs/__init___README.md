# __init__.py (LLMs) – Registro e Inicialización de Adaptadores de Lenguaje

## Descripción General
Este archivo se encarga de centralizar y documentar todos los adaptadores de generación de lenguaje disponibles (remotos y locales) en el sistema RAG.

## Funcionalidades Requeridas
- **Registro de Adaptadores:**  
  - Incluir y registrar adaptadores como openai_generator.py y local_llm_generator.py.
- **Interfaz Unificada:**  
  - Proveer una API que permita seleccionar el generador de respuestas adecuado basado en la configuración del sistema.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado por loader.py para inyectar el LLM correcto en el pipeline.
- **Extensibilidad:**  
  - Facilitar la incorporación de nuevos adaptadores de lenguaje sin modificar la lógica central.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para que se complete posteriormente.
- Incluir ejemplos en comentarios sobre cómo seleccionar y cargar cada adaptador.

## Conclusión
Este README detalla la estructura y requisitos para implementar el archivo __init__.py en la carpeta LLMs, asegurando una integración modular y escalable de los generadores de respuestas en RAG.
