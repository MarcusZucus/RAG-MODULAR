# interactive.py – Interfaz Interactiva REPL para el Sistema RAG

## Descripción General
El módulo interactive.py debe proporcionar una interfaz interactiva (REPL) que permita a los usuarios configurar y ejecutar el pipeline RAG de manera guiada.

## Funcionalidades Requeridas
- **Menús Dinámicos:**  
  - Mostrar opciones basadas en la metadata de los adaptadores disponibles.
  - Permitir la selección interactiva de componentes: adaptador de inputs, modelo de embeddings, generador de respuestas, vector store.
- **Validación en Tiempo Real:**  
  - Verificar que las opciones seleccionadas sean válidas y proporcionar feedback inmediato.
- **Persistencia de Configuración:**  
  - Ofrecer la posibilidad de guardar la configuración seleccionada para futuras ejecuciones.
- **Ejecución del Pipeline:**  
  - Simular o ejecutar el pipeline RAG con la configuración elegida, mostrando resultados y logs en pantalla.
- **Consulta de Servicios Externos:**  
  - Durante la configuración, permitir la consulta de core/service_detector.py para informar al usuario sobre la disponibilidad de servicios externos.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado por usuarios que prefieren una interfaz interactiva en lugar de la línea de comandos tradicional.
- **Relación con Otros Módulos:**  
  - Se integra con core/pipeline.py y utiliza plugins/metadata.py para ofrecer opciones informadas basadas en los adaptadores disponibles.

## Recomendaciones de Implementación
- El archivo debe quedar completamente vacío para su futura implementación.
- Incluir en el README ejemplos de interacciones y flujo de configuración para orientar a los desarrolladores.

## Conclusión
Este README es la guía completa para implementar interactive.py, asegurando una interfaz intuitiva, validada y persistente para la ejecución interactiva del pipeline RAG.
