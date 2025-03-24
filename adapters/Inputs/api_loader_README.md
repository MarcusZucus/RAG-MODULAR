# api_loader.py – Adaptador para Carga de Datos vía API REST

## Descripción General
El módulo api_loader.py debe encargarse de realizar llamadas a APIs REST para extraer datos en tiempo real, validarlos y normalizarlos según el esquema del sistema RAG.

## Funcionalidades Requeridas
- **Conexión a API:**  
  - Configurar autenticación (API keys, OAuth) y encabezados necesarios para la comunicación.
  - Realizar peticiones GET/POST a endpoints definidos.
- **Validación y Normalización:**  
  - Validar la respuesta contra el esquema en data/schema_docs.json utilizando utils/validation.py.
  - Transformar la información para cumplir con el formato requerido (id, texto, metadata).
- **Manejo de Errores y Reintentos:**  
  - Implementar timeouts, reintentos y manejo de excepciones en caso de fallos en la comunicación.
- **Registro de Operaciones:**  
  - Utilizar utils/logger.py para documentar el número de documentos cargados y los errores ocurridos.
- **Consulta de Servicios Externos:**  
  - Antes de realizar llamadas a APIs externas, verificar con core/service_detector.py la disponibilidad del servicio.

## Integración con el Sistema
- **Uso Principal:**  
  - Se invoca cuando la fuente de datos es un servicio externo que provee información en formato JSON.
- **Interfaz:**  
  - Debe cumplir con la interfaz definida en core/interfaces/input_source.py.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir una implementación personalizada.
- Incluir ejemplos en el README sobre el formato de respuesta esperado y posibles escenarios de error.

## Conclusión
Este README es la guía exhaustiva para la implementación de api_loader.py, garantizando que la carga de datos vía API se realice de forma segura, validada y eficiente.
