# input_source.py – Interfaz para Cargadores de Datos

## Descripción General
Define el contrato que deben implementar todos los módulos encargados de la carga de datos en el sistema RAG.

## Funcionalidades Requeridas
- **Método load():**  
  - Debe cargar y retornar una lista de documentos normalizados.
  - Cada documento debe incluir los campos id, texto y metadata.
  - Implementar manejo de excepciones en caso de errores o datos mal formateados.
  
## Integración con el Sistema
- **Uso Principal:**  
  - Implementado por adaptadores en adapters/Inputs/ como json_loader.py, sql_loader.py y api_loader.py.
- **Validación:**  
  - Se integrará con utils/validation.py para asegurar el cumplimiento del esquema definido.
- **Referencia a Servicios Externos:**  
  - Antes de realizar cargas desde fuentes externas, se debe consultar core/service_detector.py.

## Recomendaciones de Implementación
- El archivo debe estar completamente vacío para que la implementación se realice de forma manual.
- Incluir en el README ejemplos de casos de éxito y de error para orientar a los desarrolladores.

## Conclusión
Este documento es la guía para la implementación de la interfaz input_source.py, asegurando que cada cargador de datos en RAG cumpla con los requisitos de formato y robustez.
