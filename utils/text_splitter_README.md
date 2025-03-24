# text_splitter.py – Módulo para División de Textos en Chunks

## Descripción General
El módulo text_splitter.py debe dividir textos largos en segmentos (chunks) de tamaño óptimo para el procesamiento por LLMs y generación de embeddings.

## Funcionalidades Requeridas
- **División Flexible:**  
  - Permitir la división por tokens, caracteres o párrafos.
  - Configurar parámetros como tamaño máximo de chunk y solapamiento entre segmentos.
- **Validación de Chunks:**  
  - Asegurar que cada chunk cumpla con condiciones mínimas de relevancia y tamaño.
- **Registro y Métricas:**  
  - Documentar el número de chunks generados y los tiempos de procesamiento mediante utils/logger.py.

## Integración con el Sistema
- **Uso Principal:**  
  - Es invocado por el pipeline para fragmentar textos antes del cálculo de embeddings o generación de respuestas.
- **Compatibilidad:**  
  - Debe funcionar de manera transparente con otros módulos que procesen textos largos.

## Recomendaciones de Implementación
- El archivo debe quedar vacío para permitir que se implemente la lógica posteriormente.
- Incluir ejemplos de entrada y salida en la documentación interna (comentarios) para facilitar pruebas.

## Conclusión
Este README proporciona una guía completa para la implementación de text_splitter.py, asegurando que la división de textos se realice de manera eficiente y configurable en el sistema RAG.
