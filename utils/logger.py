import logging
import os

# Crear un logger global para el proyecto con el nombre "RAGLogger"
logger = logging.getLogger("RAGLogger")

# Configurar el logger solo si aún no tiene handlers (para evitar configuraciones duplicadas)
if not logger.handlers:
    # Permitir configurar el nivel de log mediante la variable de entorno "RAG_LOG_LEVEL"
    log_level_str = os.getenv("RAG_LOG_LEVEL", "DEBUG").upper()
    # Validar que el nivel de log sea válido, de lo contrario se usará DEBUG por defecto
    log_level = getattr(logging, log_level_str, logging.DEBUG)
    logger.setLevel(log_level)

    # Crear un StreamHandler para salida a consola
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)

    # Definir un formato estandarizado para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    # Añadir el handler al logger
    logger.addHandler(stream_handler)
