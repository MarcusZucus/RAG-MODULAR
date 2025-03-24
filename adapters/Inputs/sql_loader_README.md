# sql_loader.py – Adaptador para Carga de Datos desde Bases de Datos SQL

## Descripción General
El módulo sql_loader.py debe establecer una conexión segura a una base de datos SQL para extraer documentos y transformarlos al formato estándar requerido por el sistema RAG.

## Funcionalidades Requeridas
- **Conexión Segura:**  
  - Utilizar mecanismos de conexión seguros (ORM o drivers nativos) con credenciales y pooling.
- **Extracción de Datos:**  
  - Ejecutar consultas parametrizadas para prevenir inyecciones SQL.
  - Mapear los resultados obtenidos al formato estándar (campos: id, texto, metadata).
- **Manejo de Transacciones:**  
  - Implementar transacciones y rollbacks para garantizar la integridad de los datos.
- **Registro y Logging:**  
  - Registrar tiempos de ejecución y posibles errores mediante utils/logger.py.
- **Consulta de Servicios Externos:**  
  - Verificar mediante core/service_detector.py la disponibilidad de la base de datos antes de establecer la conexión.

## Integración con el Sistema
- **Uso Principal:**  
  - Se utiliza en entornos donde la fuente de datos es una base de datos SQL.
- **Validación:**  
  - Debe integrarse con utils/validation.py para validar la estructura de los documentos extraídos.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para que la implementación se realice conforme a estas directrices.
- Documentar ejemplos de consultas y manejo de errores en el código interno (comentarios).

## Conclusión
Este README detalla todas las expectativas para la implementación de sql_loader.py, asegurando la extracción segura y correcta de datos desde bases de datos SQL en el sistema RAG.
