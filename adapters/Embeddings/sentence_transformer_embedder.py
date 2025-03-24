"""
sentence_transformer_embedder.py – Adaptador para Generación de Embeddings con Modelos Locales de Sentence Transformers

Enfoque ultra-extendido "state-of-the-art" listo para producción:
  - Carga de modelo configurable (por variable de entorno o parámetro).
  - Soporte de batch processing y división de textos largos en chunks.
  - Caching de resultados para ahorrar cómputo (utils/cache_manager).
  - Concurrencia controlada con threading.Lock.
  - Manejo de errores y logging detallado.
  - Verificación de disponibilidad del servicio local "sentence_transformer" mediante service_detector.
  
Requisitos:
  1. pip install sentence-transformers (o transformers + la librería exacta deseada).
  2. Configurar "SENTENCE_TRANSFORMER_MODEL" en .env (por ejemplo: all-MiniLM-L6-v2).
  3. Revisar core/service_detector.py para que devuelva True si tu entorno local es válido.
"""

import os
import logging
import threading
from typing import List, Optional, Union

from core.service_detector import check_service_availability
from utils.logger import logger
from utils.cache_manager import get_cache, set_cache

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.error("La librería 'sentence-transformers' no está instalada. Usa 'pip install sentence-transformers'")
    raise RuntimeError("Falta la dependencia 'sentence-transformers' para usar sentence_transformer_embedder.")

# Lock global para la carga concurrente del modelo
_model_lock = threading.Lock()
_global_model = None

# Parámetros por defecto
DEFAULT_BATCH_SIZE = 16
DEFAULT_CHUNK_SIZE = 2048  # Cantidad de caracteres por chunk si se habilita la división


def create() -> str:
    """
    Función de registro que permite identificar este adaptador de embeddings.
    
    Returns:
        str: Mensaje simple de que fue creado exitosamente.
    """
    return "sentence_transformer_embedder_creado"


def _load_model(model_name: str) -> SentenceTransformer:
    """
    Carga (o reutiliza) el modelo global de SentenceTransformer.

    Args:
        model_name (str): Nombre o ruta del modelo local de HuggingFace.

    Returns:
        SentenceTransformer: Instancia del modelo lista para generar embeddings.
    """
    global _global_model

    if _global_model is not None:
        # Modelo ya cargado
        return _global_model

    with _model_lock:
        # Verificar de nuevo si otro hilo lo cargó mientras esperábamos
        if _global_model is None:
            try:
                logger.info(f"Cargando modelo SentenceTransformer: {model_name}")
                _global_model = SentenceTransformer(model_name)
                logger.info("Modelo SentenceTransformer cargado con éxito.")
            except Exception as e:
                logger.error(f"Error al cargar el modelo de SentenceTransformer '{model_name}': {e}")
                raise RuntimeError(f"Fallo al cargar modelo local: {e}")
    return _global_model


def embed(
    texts: List[str],
    model_name: Optional[str] = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    enable_chunking: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> List[List[float]]:
    """
    Genera embeddings para una lista de textos utilizando un modelo local de Sentence Transformers.
    
    Args:
        texts (list[str]): Lista de textos.
        model_name (str, opcional): Nombre o ruta del modelo. Si no se especifica, se toma de la ENV SENTENCE_TRANSFORMER_MODEL.
        batch_size (int): Tamaño de batch para procesar en cada pasada.
        enable_chunking (bool): Si es True, cada texto se divide en chunks de longitud `chunk_size` y se promedian.
        chunk_size (int): Longitud máxima de cada chunk si enable_chunking=True.

    Returns:
        list[list[float]]: Lista de embeddings (cada uno es un vector list[float]).

    Raises:
        RuntimeError: Si el modelo no está disponible o si check_service_availability("sentence_transformer") da False.
    """
    # Verificar disponibilidad del "servicio" local
    if not check_service_availability("sentence_transformer"):
        raise RuntimeError("Servicio 'sentence_transformer' no disponible o no configurado correctamente.")

    if not model_name:
        model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

    # Crear una clave de caché única, basada en los textos, chunking y el modelo
    cache_key = f"sent_trans_embed:{model_name}:{enable_chunking}:{hash(tuple(texts))}"
    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("Embeddings recuperados de caché (SentenceTransformer).")
        return cached

    # Carga (o reuso) del modelo local
    model = _load_model(model_name)

    # Opcional: dividir cada texto en chunks y generar embedding final promediado
    def chunk_text(text: str) -> List[str]:
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    final_embeddings = []
    try:
        if enable_chunking:
            # Caso: cada texto -> varios chunks -> se promedian
            # Recolectamos un array temporal de embeddings
            for text in texts:
                if len(text) <= chunk_size:
                    # Directo, sin partición
                    emb = model.encode([text], batch_size=batch_size)[0]
                    final_embeddings.append(emb.tolist())
                else:
                    subtexts = chunk_text(text)
                    sub_embs = model.encode(subtexts, batch_size=batch_size)
                    # Hacemos un promedio de cada vector para obtener uno solo
                    # (Podrías usar la lógica que prefieras: sum, average, weighted, etc.)
                    sum_emb = sum(sub_embs)
                    merged = (sum_emb / len(sub_embs)).tolist()
                    final_embeddings.append(merged)
        else:
            # Caso normal: encode en lotes
            # Sentence Transformers internamente maneja batching si se le pasa "batch_size"
            embeddings = model.encode(texts, batch_size=batch_size)
            # "embeddings" es una lista (ndarray) de vectores
            final_embeddings = [emb.tolist() for emb in embeddings]

        # Guardar en caché
        set_cache(cache_key, final_embeddings)
        logger.info("Embeddings generados exitosamente con SentenceTransformer (caché actualizado).")
        return final_embeddings

    except Exception as e:
        logger.error(f"Error generando embeddings con SentenceTransformer: {e}")
        raise RuntimeError(f"Fallo en embed() SentenceTransformer: {e}")
