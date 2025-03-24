"""
__init__.py (VectorStores) – Registro Dinámico y Extremo de Adaptadores de Vector Stores

Características:
  - Recorrer automáticamente los archivos .py en esta carpeta (excepto __init__.py y archivos que empiecen con '_').
  - Importar cada módulo y almacenarlos en VECTORSTORE_REGISTRY bajo la clave de su nombre de archivo (sin .py).
  - Garantizar seguridad de hilos con threading.Lock.
  - Posibilidad de force_reload para recargar adaptadores en tiempo de ejecución.
  - Logs detallados para diagnosticar problemas al importar.

Integración:
  - El pipeline o loader.py pueden consultar get_available_vectorstores()
    y acceder a un adaptador en particular (p. ej. faiss_store, chroma_store).
  - Cada archivo en VectorStores debería exponer métodos como add(), search(), etc.

Uso:
  - load_vectorstores_adapters(force_reload=False) carga dinámicamente los adaptadores.
  - get_available_vectorstores() retorna el registro; si no están cargados, los carga.
"""

import os
import logging
import importlib
import threading

logger = logging.getLogger("VectorStoresInitLogger")
logger.setLevel(logging.DEBUG)

_VECTORSTORE_LOCK = threading.Lock()
VECTORSTORE_REGISTRY = {}  # { "faiss_store": module, "chroma_store": module, ... }
_LOADED = False

def load_vectorstores_adapters(force_reload: bool = False) -> None:
    """
    Escanea la carpeta adapters/VectorStores en busca de ficheros .py, importándolos
    y registrándolos en VECTORSTORE_REGISTRY. Excluye __init__.py y archivos con prefijo '_'.

    Args:
        force_reload (bool): Si True, limpia el registro y reescanea (útil si se agregan
                             adaptadores en tiempo de ejecución).
    """
    global _LOADED, VECTORSTORE_REGISTRY

    with _VECTORSTORE_LOCK:
        if _LOADED and not force_reload:
            logger.debug("Adaptadores de VectorStores ya se encuentran cargados; no se recargan.")
            return

        VECTORSTORE_REGISTRY.clear()
        current_dir = os.path.dirname(__file__)
        logger.info(f"Buscando adaptadores de VectorStores en: {current_dir}")

        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and filename != "__init__.py" and not filename.startswith("_"):
                module_name = filename[:-3]  # remover .py
                import_path = f"adapters.VectorStores.{module_name}"
                try:
                    mod = importlib.import_module(import_path)
                    VECTORSTORE_REGISTRY[module_name] = mod
                    logger.info(f"Módulo VectorStore '{module_name}' importado con éxito.")
                except Exception as e:
                    logger.error(f"Error importando '{import_path}': {e}")

        _LOADED = True

def get_available_vectorstores() -> dict:
    """
    Retorna el diccionario con los adaptadores de VectorStores disponibles.
    Si aún no están cargados, se invoca load_vectorstores_adapters() automáticamente.
    """
    if not _LOADED:
        load_vectorstores_adapters()
    return VECTORSTORE_REGISTRY
