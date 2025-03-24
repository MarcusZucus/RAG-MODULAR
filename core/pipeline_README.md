# pipeline.py – Núcleo y Coordinador del Sistema RAG

## Descripción General
Este documento describe de forma detallada las expectativas para la implementación de pipeline.py dentro del sistema RAG.  
El archivo debe ser el núcleo del sistema, orquestando el proceso completo mediante la integración de distintos adaptadores, utilidades y la detección dinámica de servicios externos.
  
## Funcionalidades Requeridas
- **Inicialización y Configuración:**  
  - Debe recibir la configuración centralizada (obtenida desde config.py) y almacenar parámetros globales.
  - Utilizar un módulo de carga dinámica (por ejemplo, loader.py) para inyectar adaptadores de inputs, embeddings, vector stores y LLMs.
- **Ciclo de Vida del Pipeline:**  
  - Método preprocess(documents): Validar y normalizar documentos asegurándose de que cada uno tenga id, texto y metadata.  
  - Método load_data(): Invocar el método .load() del adaptador de inputs y transformar la data de acuerdo al esquema definido.
  - Método compute_embeddings(texts): Calcular embeddings para cada texto, integrando un sistema de cache para evitar reprocesamientos.
  - Método store_vectors(documents, embeddings): Almacenar documentos junto a sus vectores en el vector store, permitiendo actualizaciones incrementales.
  - Método retrieve_and_generate(query): Realizar una búsqueda vectorial para recuperar documentos relevantes y generar una respuesta mediante un LLM.
- **Integración de Plugins y Manejo de Errores:**  
  - Incorporar hooks o plugins (por ejemplo, plugins/discovery.py y plugins/metadata.py) para funcionalidades adicionales y registro de métricas.
  - Implementar bloques de manejo de errores (try/except) con logging detallado a través de utils/logger.py.
- **Detección de Servicios Externos:**  
  - **Nuevo:** Antes de utilizar cualquier servicio externo (APIs, bases de datos, servicios de embeddings o LLMs), se debe consultar el módulo core/service_detector.py para verificar la disponibilidad y características del servicio.

## Integración con Otros Módulos
- **Configuración:** Se conecta con core/config.py para obtener parámetros globales.
- **Adaptadores:** Utiliza loader.py para inyectar componentes de inputs, embeddings, vector stores y LLMs.
- **Utilidades:** Emplea utils/validation.py, utils/cache_manager.py y utils/logger.py para validaciones, caching y logging.
- **Plugins:** Se integra con módulos en plugins/ para extender funcionalidades (descubrimiento, metadatos).

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío (sin código) para permitir que se complete la implementación manualmente según las especificaciones aquí descritas.
- Cada método debe tener documentación interna (docstrings) que explique su funcionalidad, parámetros y valores de retorno.
- Se debe garantizar la modularidad para que la sustitución o actualización de adaptadores no afecte el funcionamiento global del sistema.
- **Importante:** Revisar core/service_detector.py para la detección de servicios externos antes de invocar adaptadores que dependen de ellos.

## Conclusión
Este README es la guía completa para la futura implementación de pipeline.py. Cada desarrollador debe referirse a este documento para entender la arquitectura, los puntos de integración y las responsabilidades de este módulo en el proyecto RAG.
