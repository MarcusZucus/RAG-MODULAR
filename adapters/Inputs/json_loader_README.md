# json_loader.py – Adaptador para Carga de Datos desde Archivos JSON

## Descripción General
El módulo json_loader.py se encarga de cargar datos desde archivos JSON, validarlos y normalizarlos para cumplir con el esquema del sistema RAG.

## Funcionalidades Requeridas
- **Lectura Segura:**  
  - Abrir y leer archivos JSON especificados.
  - Manejar excepciones en caso de problemas de lectura.
- **Validación de Datos:**  
  - Validar cada documento contra el esquema definido en data/schema_docs.json utilizando utils/validation.py.
  - Transformar y normalizar la información para asegurar la presencia de los campos obligatorios (id, texto, metadata).
- **Registro de Operaciones:**  
  - Utilizar utils/logger.py para registrar el éxito o errores durante la carga.
- **Consulta a Servicio de Detección:**  
  - Antes de cargar datos desde fuentes externas, se debe consultar core/service_detector.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Es invocado por el pipeline para obtener documentos de ejemplo o reales en formato JSON.
- **Relación con Otros Adaptadores:**  
  - Se espera que siga el mismo contrato definido en core/interfaces/input_source.py.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para que se implemente la lógica de carga según estas especificaciones.
- Incluir en el README ejemplos de formato de archivo JSON y mensajes de error esperados.

## Conclusión
Este README proporciona la guía completa para la implementación de json_loader.py, asegurando una carga de datos robusta y estandarizada para el proyecto RAG.
