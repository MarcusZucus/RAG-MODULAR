# config.py – Gestión Centralizada de Configuración del Sistema RAG

## Descripción General
El archivo config.py es responsable de centralizar la configuración del sistema RAG. Este documento describe detalladamente lo que se espera de su implementación.

## Funcionalidades Requeridas
- **Lectura de Variables de Entorno:**  
  - Leer el archivo .env para obtener variables sensibles (p.ej., API keys, credenciales de base de datos).
- **Fusión y Validación de Configuraciones:**  
  - Combinar configuraciones provenientes de archivos de esquema (como registry/config_schema.json) y de variables de entorno.
  - Validar la configuración utilizando el esquema definido, garantizando que se respeten los tipos y campos requeridos.
- **API de Configuración:**  
  - Proveer funciones como get_config() para obtener la configuración global y update_config(new_config) para actualizarla en tiempo de ejecución.
- **Integración con Detección de Servicios:**  
  - Consultar el módulo core/service_detector.py para verificar la disponibilidad y características de servicios externos al momento de configurar el sistema.

## Integración con el Sistema
- **Módulos Dependientes:**  
  - Es utilizado por pipeline.py, loader.py y otros módulos que requieren parámetros globales.
- **Seguridad y Persistencia:**  
  - Manejar errores de lectura y garantizar que la configuración se mantenga consistente en entornos cambiantes.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para que la implementación se realice conforme a estas especificaciones.
- Cada función debe ser desarrollada con pruebas unitarias para asegurar la integridad y compatibilidad del sistema.
- Incluir comentarios internos que expliquen la lógica de fusión de configuraciones y validación contra el esquema.

## Conclusión
Este README provee la guía para implementar config.py de manera robusta y escalable, asegurando la correcta gestión de la configuración del sistema RAG.
