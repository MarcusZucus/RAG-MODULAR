# model_registry.json – Registro de Modelos y Adaptadores

## Descripción General
Este archivo JSON registra todas las combinaciones, versiones y dependencias de los componentes del sistema RAG, permitiendo controlar compatibilidades y realizar rollbacks en caso de errores.

## Funcionalidades Requeridas
- **Listado de Componentes:**  
  - Cada entrada debe incluir: name, version, dependencies y compatibility.
- **Control de Versiones:**  
  - Facilitar la identificación de incompatibilidades y permitir reversión a versiones anteriores si es necesario.
- **Auditoría y Registro:**  
  - Mantener un histórico de versiones y cambios para facilitar la auditoría del sistema.

## Integración con el Sistema
- **Uso Principal:**  
  - Es consultado por config.py y loader.py para validar la compatibilidad entre componentes.
- **Actualización Dinámica:**  
  - Permitir que el sistema realice actualizaciones o rollbacks basados en la información de este registro.

## Recomendaciones de Implementación
- No debe ser modificado manualmente sin seguir una política de versionado estricta.
- Incluir ejemplos y comentarios en el archivo para guiar futuras actualizaciones.

## Conclusión
Este README ofrece una guía detallada para el manejo de model_registry.json, asegurando un control preciso y auditable de las versiones y dependencias en el sistema RAG.
