# chroma_store.py – Adaptador para Gestión de Índices con ChromaDB

## Descripción General
El módulo chroma_store.py debe gestionar índices vectoriales utilizando ChromaDB.  
Se espera que implemente funciones para la inserción, actualización y búsqueda de documentos, manteniendo un historial para auditoría.

## Funcionalidades Requeridas
- **Inicialización y Configuración:**  
  - Conectar a ChromaDB y configurar parámetros de persistencia.
- **Inserción de Documentos:**  
  - Método add(document, vector) que almacene la información en un índice simulado o real.
- **Búsqueda de Documentos:**  
  - Método search(query_vector, k) para recuperar los k documentos más cercanos.
- **Manejo de Versiones y Auditoría:**  
  - Registrar cambios, versiones y proporcionar mecanismos de rollback en caso de errores.
- **Consulta de Servicios Externos:**  
  - Antes de realizar operaciones, consultar core/service_detector.py para validar la conexión al servicio.

## Integración con el Sistema
- **Uso Principal:**  
  - Se utiliza en el pipeline como alternativa al adaptador FAISS para indexación vectorial.
- **Interfaz:**  
  - Debe adherirse al contrato definido en core/interfaces/vector_store.py.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para ser completado manualmente.
- Incluir ejemplos de escenarios de búsqueda y manejo de versiones en la documentación interna.

## Conclusión
Este README proporciona una guía detallada para la implementación de chroma_store.py, asegurando una gestión robusta y escalable de índices vectoriales mediante ChromaDB en el sistema RAG.
