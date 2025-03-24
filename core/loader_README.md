# loader.py – Módulo de Inyección Dinámica de Adaptadores

## Descripción General
loader.py debe implementar un sistema de inyección de dependencias utilizando un patrón factory.  
Este documento detalla en profundidad las funcionalidades y requisitos para la correcta implementación del módulo.

## Funcionalidades Requeridas
- **Descubrimiento Dinámico:**  
  - Escanear recursivamente la carpeta adapters/ para identificar módulos y submódulos disponibles.
  - Extraer metadatos de cada adaptador utilizando convenciones (por ejemplo, mediante decoradores o archivos de metadata).
- **Validación e Instanciación:**  
  - Verificar que cada adaptador cumpla con la interfaz requerida (ver archivos en core/interfaces/).
  - Instanciar el adaptador a través de una función estándar (por ejemplo, create()) y configurarlo según la configuración global.
- **Registro y Logging:**  
  - Registrar cada carga de componente mediante utils/logger.py, incluyendo detalles como versiones, dependencias y posibles conflictos.
- **Integración con el Servicio de Detección:**  
  - Antes de cargar adaptadores que dependen de servicios externos, consultar core/service_detector.py para validar la disponibilidad del servicio.

## Integración con el Sistema
- **Uso Principal:**  
  - Es utilizado en pipeline.py para inyectar adaptadores de inputs, embeddings, vector stores y LLMs.
- **Interacción con Plugins:**  
  - Se debe integrar con plugins/metadata.py para validar la metadata de cada adaptador.

## Recomendaciones de Implementación
- El archivo debe estar vacío para ser completado manualmente según estas instrucciones.
- Incluir comentarios y placeholders donde se requiera la integración con otros módulos.
- Garantizar la robustez del mecanismo de descubrimiento para evitar errores en tiempo de ejecución.

## Conclusión
Este README debe servir como guía completa para la futura implementación de loader.py, asegurando una inyección de dependencias dinámica, modular y escalable en el sistema RAG.
