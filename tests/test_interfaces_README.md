# test_interfaces.py – Pruebas Unitarias de Interfaces

## Descripción General
El archivo test_interfaces.py debe contener pruebas unitarias que aseguren que cada adaptador cumple con las interfaces definidas en:
  - core/interfaces/base.py
  - core/interfaces/input_source.py
  - core/interfaces/embedding_model.py
  - core/interfaces/vector_store.py
  - core/interfaces/llm_model.py

## Funcionalidades Requeridas
- **Validación de Métodos:**  
  - Verificar la existencia y correcta implementación de métodos obligatorios en cada adaptador.
- **Pruebas de Retorno:**  
  - Comprobar que los tipos de retorno y el manejo de excepciones sean consistentes con lo especificado.
- **Documentación de Casos de Éxito y Error:**  
  - Registrar en los tests ejemplos de implementaciones exitosas y casos donde se esperen fallos.
- **Referencia a Servicios Externos:**  
  - Incluir pruebas para verificar que, en caso de que un adaptador requiera un servicio externo, se consulte correctamente core/service_detector.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado para asegurar que la base del sistema cumple con los contratos de interfaz.
- **Relación con Otros Módulos:**  
  - Permite detectar de forma temprana discrepancias en la implementación de los adaptadores.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para permitir la implementación de pruebas personalizadas.
- Incluir en el README ejemplos de llamadas a métodos y manejo de errores esperados.

## Conclusión
Este README detalla la guía para implementar test_interfaces.py, asegurando que todas las interfaces del sistema RAG sean respetadas y probadas de forma exhaustiva.
