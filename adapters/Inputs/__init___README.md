# __init__.py (Inputs) – Registro y Inicialización de Adaptadores de Carga de Datos

## Descripción General
Este archivo se utiliza para centralizar y registrar todos los adaptadores de carga de datos (JSON, SQL, API) disponibles en la carpeta adapters/Inputs/.

## Funcionalidades Requeridas
- **Registro de Módulos:**  
  - Incluir la importación o registro de cada adaptador (por ejemplo, json_loader.py, sql_loader.py, api_loader.py).
- **Documentación y Metadatos:**  
  - Servir como punto de referencia para la selección dinámica de adaptadores mediante metadatos definidos en cada módulo.
  
## Integración con el Sistema
- **Uso Principal:**  
  - Facilitar que loader.py pueda descubrir y cargar el adaptador correcto según la configuración del sistema.
- **Extensibilidad:**  
  - Permitir la adición de nuevos adaptadores sin necesidad de modificar el código central.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para que el desarrollador lo complete según las necesidades específicas del proyecto.
- Incluir comentarios explicativos en el futuro para guiar la integración con el sistema de inyección de dependencias.

## Conclusión
Este README proporciona la guía para implementar el archivo de inicialización en adapters/Inputs/, asegurando un registro organizado y escalable de todos los cargadores de datos.
