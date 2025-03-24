# test_registry.py – Pruebas de Integridad del Registro de Modelos

## Descripción General
El archivo test_registry.py debe validar que model_registry.json contenga la información necesaria sin duplicados y que se simulen correctamente escenarios de rollback ante incompatibilidades.

## Funcionalidades Requeridas
- **Verificación de Campos:**  
  - Comprobar que cada entrada tenga los campos obligatorios: name, version, dependencies y compatibility.
- **Detección de Duplicados:**  
  - Asegurar que no existan entradas duplicadas en el registro.
- **Simulación de Rollback:**  
  - Probar escenarios en los que la incompatibilidad entre versiones desencadene un rollback o alerta.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado para garantizar la consistencia y robustez del sistema a través del control de versiones.
- **Interacción:**  
  - Se relaciona con config.py y loader.py para la validación de la configuración y compatibilidades.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir la implementación personalizada.
- Incluir en el README ejemplos de escenarios de prueba y mensajes de error esperados.

## Conclusión
Este README proporciona la guía para implementar test_registry.py, asegurando que el registro de modelos mantenga la integridad y permita una fácil auditoría y reversión en el sistema RAG.
