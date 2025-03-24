# Proyecto RAG – Versión 2.0 Ultra-Extendida

## Descripción General
Proyecto RAG es un sistema modular para la generación de respuestas que combina técnicas de búsqueda semántica con modelos de lenguaje avanzados.  
La arquitectura se compone de múltiples módulos y adaptadores que permiten una integración flexible, escalable y segura.

## Estructura del Proyecto
- **core/**: Núcleo del sistema y orquestador. ¡Ahora incluye también service_detector.py para la detección dinámica de servicios externos!
- **adapters/**: Implementaciones intercambiables para:
    - Inputs (carga de datos desde JSON, SQL, API)
    - Embeddings (generación de vectores numéricos)
    - Vector Stores (indexación y búsqueda semántica)
    - LLMs (generación de respuestas)
- **plugins/**: Extensiones para descubrimiento y validación de metadatos.
- **registry/**: Control de versiones y compatibilidades de los modelos y adaptadores.
- **utils/**: Funciones y utilidades comunes para validación, logging, cache y métricas.
- **api/**: Interfaz RESTful basada en FastAPI para exponer el sistema.
- **cli/**: Herramientas de línea de comandos para ejecución y configuración.
- **dashboard/**: Panel visual para monitoreo y administración.
- **tests/**: Pruebas unitarias e integradas para garantizar la calidad del sistema.
- **data/**: Documentos de ejemplo y esquemas de validación.
- **security/**, **monitoring/**, **scalability/**: Módulos adicionales para cubrir aspectos críticos de seguridad, monitoreo y tolerancia a fallos.

## Cómo Empezar
1. Instalar las dependencias con:  
   pip install -r requirements.txt
2. Configurar las variables de entorno en el archivo .env.
3. Ejecutar la aplicación API con:  
   uvicorn api.app:app --host 0.0.0.0 --port 8000
4. Revisar los scripts en cli/ para ejecuciones no interactivas o interactivas.

## Contribución
- Se aceptan contribuciones siguiendo las guías de estilo y la estructura modular del proyecto.
- Consultar los archivos README de cada carpeta para obtener detalles sobre la funcionalidad e integración de cada módulo.
- **Importante:** Dado que el sistema es universal y dinámico, se debe consultar siempre el módulo core/service_detector.py antes de utilizar servicios externos, lo que permite adaptar el sistema a cualquier entorno de producción sin modificar el código fuente.

## Documentación
Este repositorio incluye documentación ultra detallada para cada módulo, asegurando que cualquier desarrollador pueda comprender, extender y mantener el sistema de manera eficiente y sin ambigüedades.

## Conclusión
Proyecto RAG es una herramienta robusta y escalable diseñada para la generación de respuestas, con una arquitectura modular que facilita la integración, actualización y mantenimiento. Su enfoque universal permite adaptarlo a cualquier entorno de producción de manera plug & play.
