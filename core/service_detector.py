import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    # Configuración básica de consola
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_service_availability(service_name: str) -> bool:
    """
    Verifica la disponibilidad del servicio especificado.
    
    Esta función implementa chequeos diferenciados según el tipo de servicio:
    
      - Para servicios basados en OpenAI (por ejemplo, 'openai', 'openai_generator', 'openai_embedder'),
        se verifica que la variable de entorno OPENAI_API_KEY esté definida.
      - Para adaptadores de vector store (por ejemplo, 'faiss_store', 'chroma_store'), se asume que
        si la librería está instalada, el servicio es local y está disponible.
      - Para generadores locales (por ejemplo, 'local_llm_generator', 'gguf'),
        se comprueba que la variable de entorno GGUF_MODEL_PATH esté definida y apunte a un archivo existente.
      - Para el pre‑RAG (service_name = "pre_rag"), se verifica que exista el directorio "pre_rag"
        y que contenga al menos un archivo JSON.
      - Para la base de datos (por ejemplo, 'db' o 'database'), se comprueba que DB_CONNECTION esté configurada.
      - Para otros servicios, se asume que están disponibles, pero se registra una información.

    Args:
        service_name (str): Nombre del servicio a verificar.

    Returns:
        bool: True si el servicio se considera disponible, False en caso contrario.
    """
    try:
        service = service_name.lower()
        if service in {"openai", "openai_generator", "openai_embedder"}:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY no está configurada.")
                return False
            return True

        elif service in {"faiss_store", "chroma_store"}:
            # Se asume que la instalación local de la librería implica disponibilidad.
            return True

        elif service in {"local_llm_generator", "gguf"}:
            model_path = os.getenv("GGUF_MODEL_PATH")
            if not model_path:
                logger.error("GGUF_MODEL_PATH no está configurada para el modelo gguf.")
                return False
            if not os.path.exists(model_path):
                logger.error(f"El modelo gguf no se encontró en la ruta especificada: {model_path}")
                return False
            return True

        elif service == "pre_rag":
            pre_rag_dir = os.path.join(os.getcwd(), "pre_rag")
            if not os.path.isdir(pre_rag_dir):
                logger.error("El directorio 'pre_rag' no existe.")
                return False
            json_files = [f for f in os.listdir(pre_rag_dir) if f.endswith(".json")]
            if not json_files:
                logger.error("No se encontraron archivos JSON en el directorio 'pre_rag'.")
                return False
            return True

        elif service in {"db", "database"}:
            db_conn = os.getenv("DB_CONNECTION")
            if not db_conn:
                logger.error("DB_CONNECTION no está configurada.")
                return False
            return True

        else:
            logger.info(f"No se definieron chequeos específicos para el servicio '{service_name}'. Se asume disponibilidad.")
            return True

    except Exception as e:
        logger.error(f"Error al verificar disponibilidad del servicio '{service_name}': {e}")
        return False
