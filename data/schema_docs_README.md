# schema_docs.json – Esquema para Validación de Documentos en el Sistema RAG

## Descripción General
Este archivo define el esquema JSON que deben cumplir todos los documentos procesados por el sistema RAG.  
Establece los tipos, restricciones y campos obligatorios para garantizar la integridad y consistencia de los datos.

## Estructura del Esquema
- **id:**  
  - Tipo: string.  
  - Descripción: Identificador único.
- **texto:**  
  - Tipo: string.  
  - Restricción: No debe estar vacío.
  - Descripción: Contenido principal del documento.
- **metadata:**  
  - Tipo: object.  
  - Propiedades:  
    - **origen:** string (obligatorio).
    - **fecha:** string con formato date (obligatorio).
    - **categoría:** string (opcional).
  
## Funcionalidades y Uso
- **Validación Automática:**  
  - Utilizado por utils/validation.py para asegurar que cada documento ingresado cumpla con este formato.
- **Flexibilidad y Extensibilidad:**  
  - Permite la incorporación de nuevos campos en el futuro sin afectar la validación de los documentos existentes.

## Recomendaciones de Implementación
- No modificar la estructura sin actualizar las validaciones correspondientes en el sistema.
- Incluir ejemplos y casos de prueba en la documentación interna para facilitar futuras modificaciones.

## Conclusión
Este README es la guía completa para entender y mantener el esquema de validación en el sistema RAG, garantizando la calidad de los datos en el sistema.
