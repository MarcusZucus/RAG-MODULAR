# discovery.py – Plugin de Descubrimiento de Adaptadores

## Descripción General
El módulo discovery.py debe encargarse de escanear recursivamente la carpeta adapters/ para detectar y registrar todos los módulos disponibles.

## Funcionalidades Requeridas
- **Escaneo de Directorios:**  
  - Recorrer de forma recursiva la carpeta adapters/ y detectar archivos .py (excluyendo los __init__.py).
- **Extracción de Metadatos:**  
  - Utilizar convenciones y posiblemente integrarse con plugins/metadata.py para extraer y validar metadatos (nombre, versión, dependencias, etc.).
- **Registro y Auditoría:**  
  - Registrar el número de módulos descubiertos y cualquier duplicidad o error en la extracción.
- **API para Consulta:**  
  - Proveer funciones para que otros módulos (CLI, dashboard, tests) puedan consultar el estado y la metadata de los adaptadores.
- **Referencia a Servicios Externos:**  
  - Opcionalmente, detectar adaptadores que dependan de servicios externos consultando core/service_detector.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Es invocado por loader.py para obtener información sobre los adaptadores disponibles.
- **Colaboración con Metadata:**  
  - Trabajar conjuntamente con plugins/metadata.py para validar la información extraída.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir su implementación manual.
- Documentar internamente la estructura de directorios y la lógica de extracción de metadatos.

## Conclusión
Este README es la guía para la implementación de discovery.py, asegurando un sistema robusto para el descubrimiento y registro dinámico de adaptadores en el proyecto RAG.
