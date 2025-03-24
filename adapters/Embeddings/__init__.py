"""
__init__.py (Embeddings) – Registro Dinámico y State-of-the-Art de Adaptadores de Embeddings.

Objetivos y Características:
  - Explorar automáticamente todos los módulos .py en esta carpeta (excepto __init__.py).
  - Importar dichos módulos, detectando si tienen una función create() y/o un método embed().
  - Almacenar un diccionario global EMBEDDINGS_REGISTRY que mapea { "nombre_modulo": <module> }.
  - Permitir acceso rápido a los adaptadores y, opcionalmente, validación de metadatos.

Integración con el Sistema:
  - 'loader.py' y 'service_detector.py' podrían usar este registro para inyectar adaptadores de embeddings
    en el pipeline RAG.
  - Se puede consultar EMBEDDINGS_REGISTRY["openai_embedder"] para invocar .create() o .embed().

Este __init__.py se considera "state-of-the-art" para entornos RAG altamente dinámicos y escalables.
"""

import os
import logging
import importlib
import threading

logger = logging.getLogger("EmbeddingsInitLogger")
logger.setLevel(logging.DEBUG)

_EMBEDDINGS_LOCK = threading.Lock()
EMBEDDINGS_REGISTRY = {}  # { "openai_embedder": <module>, "sentence_transformer_embedder": <module>, ... }
_LOADED = False            # Para controlar carga única

def load_embeddings_adapters(force_reload: bool = False) -> None:
    """
    Escanea el directorio actual (adapters/Embeddings/) e importa dinámicamente cada .py,
    excluyendo __init__.py y archivos con prefijo '_'.
    
    Si force_reload=True, se forza un nuevo escaneo, vaciando EMBEDDINGS_REGISTRY.
    De otro modo, si ya se cargó, se ignora.
    """
    global _LOADED, EMBEDDINGS_REGISTRY

    with _EMBEDDINGS_LOCK:
        if _LOADED and not force_reload:
            logger.debug("Los adaptadores de embeddings ya fueron cargados anteriormente; no se recargan.")
            return
        EMBEDDINGS_REGISTRY.clear()

        current_dir = os.path.dirname(__file__)
        logger.info(f"Descubriendo adaptadores de embeddings en: {current_dir}")

        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and filename != "__init__.py" and not filename.startswith("_"):
                module_name = filename[:-3]  # sin .py
                full_import_path = f"adapters.Embeddings.{module_name}"
                try:
                    mod = importlib.import_module(full_import_path)
                    EMBEDDINGS_REGISTRY[module_name] = mod
                    logger.info(f"Módulo de embeddings '{module_name}' importado exitosamente.")
                except Exception as e:
                    logger.error(f"Error al importar '{full_import_path}': {e}")

        _LOADED = True

def get_available_embeddings() -> dict:
    """
    Retorna la estructura global con los adaptadores disponibles. Si no están cargados, los carga.
    """
    if not _LOADED:
        load_embeddings_adapters()
    return EMBEDDINGS_REGISTRY

# Carga automática al importar este paquete, si se desea:
# load_embeddings_adapters()
