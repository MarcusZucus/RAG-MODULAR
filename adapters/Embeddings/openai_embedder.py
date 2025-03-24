import os
import logging
import openai
from utils.cache_manager import get_cache, set_cache

logger = logging.getLogger("RAGLogger")

def create():
    """
    Función de registro que permite identificar este adaptador de embeddings.
    
    Returns:
        str: "openai_embedder_creado"
    """
    return "openai_embedder_creado"

def embed(texts, model="text-embedding-ada-002", cache_ttl=3600):
    """
    Genera embeddings para una lista de textos utilizando la API de OpenAI.
    
    Args:
        texts (list[str]): Lista de textos a convertir en vectores.
        model (str): Modelo de embeddings a utilizar. Por defecto, "text-embedding-ada-002".
        cache_ttl (int): Tiempo en segundos para mantener el resultado en caché.
        
    Returns:
        list: Lista de vectores de embeddings.
        
    Raises:
        RuntimeError: Si OPENAI_API_KEY no está configurada o si ocurre algún error en la llamada a la API.
    """
    # Verificar la existencia de la API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY no está configurada.")
        raise RuntimeError("OPENAI_API_KEY no está configurada.")
    openai.api_key = openai_api_key

    # Crear una clave única para la caché basada en los textos y el modelo
    cache_key = f"openai_embedder:{hash(tuple(texts))}:{model}"
    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("Embeddings recuperados de caché.")
        return cached

    try:
        logger.info("Llamando a la API de OpenAI para generar embeddings.")
        response = openai.Embedding.create(input=texts, model=model)
        # Se espera que la respuesta tenga la forma: {"data": [{"embedding": [...]}, ...]}
        embeddings = [item["embedding"] for item in response["data"]]
        # Almacenar en caché
        set_cache(cache_key, embeddings, ttl=cache_ttl)
        logger.info("Embeddings generados y almacenados en caché.")
        return embeddings
    except Exception as e:
        logger.error(f"Error en OpenAI embedder: {e}")
        raise RuntimeError(f"Error generando embeddings: {e}")
