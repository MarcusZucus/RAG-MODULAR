# Dockerfile – Guía para Construir la Imagen Docker del Proyecto RAG

## Descripción General
Este archivo define el proceso de construcción de la imagen Docker para el sistema RAG utilizando un enfoque multi-stage build, optimizando el tamaño y la seguridad de la imagen final.

## Funcionalidades Requeridas
- **Instalación de Dependencias:**  
  - Descargar e instalar todas las dependencias definidas en requirements.txt.
- **Copia de Artefactos:**  
  - Copiar únicamente lo necesario para la ejecución en la imagen final, minimizando el tamaño.
- **Configuración de la Aplicación:**  
  - Configurar el usuario no root y exponer el puerto 8000 para la API.
- **Ejecución del Contenedor:**  
  - Definir el entrypoint para iniciar la aplicación con Uvicorn.

## Integración con el Sistema
- **Uso Principal:**  
  - Facilitar el despliegue del sistema RAG en entornos de producción utilizando Docker.
- **Relación con docker-compose:**  
  - Se utiliza en conjunto con docker-compose.yml para configurar un entorno multi-contenedor.

## Recomendaciones de Implementación
- Mantener el archivo actualizado conforme se añadan nuevas dependencias o se modifiquen las configuraciones del entorno.
- Incluir comentarios en el archivo para explicar cada etapa del proceso.

## Conclusión
Este README es la guía completa para entender y utilizar el Dockerfile en el proyecto RAG, asegurando una construcción segura y eficiente de la imagen Docker.
