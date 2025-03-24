# Proyecto RAG – Versión 2.0 Ultra-Extendida

## Visión General
Esta guía principal describe en detalle la estructura, instalación y uso del sistema RAG.  
Se incluyen diagramas, ejemplos prácticos y una descripción completa de cada módulo para facilitar el trabajo de desarrollo y mantenimiento.

## Estructura del Proyecto
- **core/**: Contiene el núcleo del sistema, la lógica de orquestación y la detección dinámica de servicios externos mediante service_detector.py.
- **adapters/**: Incluye adaptadores para:
    - Carga de datos (Inputs: JSON, SQL, API)
    - Generación de embeddings (OpenAI, locales)
    - Indexación y búsqueda (FAISS, ChromaDB)
    - Generación de respuestas (LLMs, tanto remotos como locales)
- **plugins/**: Sistema de plugins para descubrimiento, validación y extensión de funcionalidades.
- **registry/**: Control de versiones y compatibilidades, facilitando rollbacks y auditorías.
- **utils/**: Funciones comunes para validación, logging, cache y métricas.
- **api/**: Interfaz RESTful basada en FastAPI, con documentación interactiva.
- **cli/**: Herramientas de línea de comandos para ejecuciones no interactivas e interactivas.
- **dashboard/**: Panel visual para monitoreo en tiempo real.
- **tests/**: Conjunto de pruebas unitarias e integradas para asegurar la calidad y robustez del sistema.
- **data/**: Archivos de ejemplo y esquemas para la validación de documentos.
- **security/**, **monitoring/**, **scalability/**: Módulos adicionales para cubrir aspectos críticos de seguridad, monitoreo y tolerancia a fallos.

## Cómo Empezar
- Consultar README.md para instrucciones básicas de instalación y ejecución.
- Revisar cada README en las carpetas correspondientes para entender la funcionalidad e integración de cada módulo.
- Seguir las guías de contribución para mantener la coherencia y calidad del proyecto.

## Conclusión
Esta documentación integral asegura que cualquier desarrollador pueda entender y contribuir al proyecto RAG de manera efectiva, garantizando una herramienta modular, escalable y segura para la generación de respuestas. La integración del módulo core/service_detector.py refuerza el enfoque universal y flexible del sistema.
