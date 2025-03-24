# example_docs.json – Documentos de Ejemplo para el Sistema RAG

## Descripción General
Este archivo contiene ejemplos de documentos que sirven para pruebas, demostraciones y validaciones en el sistema RAG.

## Estructura de los Documentos
- **id:** Identificador único del documento.
- **texto:** Contenido principal que será procesado.
- **metadata:** Información adicional que puede incluir origen, fecha, categoría y otros atributos relevantes.

## Funcionalidades y Uso
- **Plantilla de Datos:**  
  - Sirve como ejemplo del formato que deben seguir todos los documentos.
- **Validación:**  
  - Es utilizado por utils/validation.py para comprobar que cada documento cumpla con el esquema definido.
- **Pruebas Unitarias:**  
  - Los adaptadores y el pipeline utilizan estos ejemplos para validar la correcta integración y procesamiento de datos.

## Recomendaciones de Implementación
- No modificar la estructura de este archivo sin actualizar el esquema de validación en data/schema_docs.json.
- Incluir ejemplos adicionales si se requieren nuevos campos en el futuro.

## Conclusión
Este README proporciona una guía detallada para entender y utilizar example_docs.json, asegurando que el formato de los datos sea consistente en todo el sistema RAG.
