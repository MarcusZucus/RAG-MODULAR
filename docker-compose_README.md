# docker-compose.yml – Orquestación Multi-Contenedor del Proyecto RAG

## Descripción General
El archivo docker-compose.yml define la configuración para desplegar el sistema RAG en un entorno multi-contenedor, integrando la API, la base de datos y el dashboard de monitoreo.

## Funcionalidades Requeridas
- **Definición de Servicios:**  
  - Configurar servicios para la API (FastAPI), la base de datos (PostgreSQL) y el dashboard.
- **Configuración de Redes y Volúmenes:**  
  - Establecer redes internas y volúmenes persistentes (por ejemplo, para la base de datos).
- **Variables de Entorno:**  
  - Pasar las variables de entorno necesarias a cada servicio, garantizando la seguridad y configuración correcta.
- **Dependencias entre Servicios:**  
  - Establecer dependencias (depends_on) para asegurar que los servicios se inicien en el orden correcto.

## Integración con el Sistema
- **Uso Principal:**  
  - Facilitar el despliegue y escalabilidad del sistema RAG en entornos de producción.
- **Relación con Dockerfile:**  
  - Se utiliza junto con el Dockerfile para construir y desplegar la imagen de la API.

## Recomendaciones de Implementación
- Mantener el archivo actualizado conforme se integren nuevos servicios o se modifiquen las configuraciones.
- Documentar cada servicio y su rol dentro del sistema en este README.

## Conclusión
Este README es la guía completa para implementar y utilizar docker-compose.yml, asegurando una orquestación efectiva y escalable de los distintos componentes del sistema RAG.
