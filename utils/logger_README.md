# logger.py – Módulo de Logging Centralizado

## Descripción General
El módulo logger.py debe proporcionar funciones para registrar eventos, errores y métricas en el sistema RAG, utilizando diferentes niveles de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Funcionalidades Requeridas
- **Configuración del Logger:**  
  - Establecer un formato estandarizado que incluya timestamp, nivel de log y mensaje.
- **Funciones de Registro:**  
  - Proveer funciones específicas para cada nivel (debug, info, warning, error, critical).
- **Prevención de Duplicados:**  
  - Evitar la duplicación de mensajes y gestionar la salida tanto en consola como en archivos, según la configuración.
- **Integración con el Sistema:**  
  - Debe ser utilizado por la mayoría de los módulos para asegurar la trazabilidad y facilitar la depuración.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para su implementación manual.
- Incluir ejemplos de configuración y uso en la documentación interna (comentarios).

## Conclusión
Este README es la guía para implementar logger.py, garantizando que el sistema RAG cuente con un mecanismo robusto y consistente de logging para la monitorización y depuración.
