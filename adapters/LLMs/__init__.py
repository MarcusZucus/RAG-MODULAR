"""
__init__.py (LLMs) – Registro Dinámico y Ultra-Extremo de Adaptadores de LLM

Características:
  - Explorar automáticamente los archivos .py (excepto __init__.py, con prefijo "_") en la carpeta actual.
  - Importar dichos módulos, detectando su disponibilidad y agregándolos a LLM_REGISTRY.
  - Manejar concurrencia con threading.Lock para entornos multihilo.
  - Controlar recarga (force_reload) para escenarios en donde se agregan / modifican adaptadores de LLM en ejecución.
  - Proveer funciones get_available_llms() y load_llms_adapters() para un pipeline RAG universal.

Integración:
  - El pipeline u otros módulos pueden consultar get_available_llms() y luego escoger un adaptador, 
    invocando métodos como generate() o create() según corresponda.
  - Se aconseja que cada archivo .py en LLMs contenga, al menos, una función create() o un LLMModel subclase.
"""

import os
import logging
import importlib
import threading

logger = logging.getLogger("LLMsInitLogger")
logger.setLevel(logging.DEBUG)

_LLMS_LOCK = threading.Lock()
LLM_REGISTRY = {}   # { "openai_generator": <module>, "local_llm_generator": <module>, ... }
_LOADED = False     # Para indicar si la carga inicial ya se efectuó

def load_llms_adapters(force_reload: bool = False) -> None:
    """
    Escanea la carpeta (adapters/LLMs) e importa dinámicamente cada módulo .py,
    excluyendo __init__.py y archivos con prefijo '_'. 
    Registra el resultado en LLM_REGISTRY.

    Args:
        force_reload (bool): Si True, se fuerza la recarga limpiando el registro y reescaneando.
    """
    global _LOADED, LLM_REGISTRY

    with _LLMS_LOCK:
        if _LOADED and not force_reload:
            logger.debug("Adaptadores de LLM ya estaban cargados; se omite recarga.")
            return

        LLM_REGISTRY.clear()
        current_dir = os.path.dirname(__file__)
        logger.info(f"Buscando adaptadores de LLM en: {current_dir}")

        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and filename != "__init__.py" and not filename.startswith("_"):
                module_name = filename[:-3]  # sin .py
                import_path = f"adapters.LLMs.{module_name}"
                try:
                    mod = importlib.import_module(import_path)
                    LLM_REGISTRY[module_name] = mod
                    logger.info(f"Módulo LLM '{module_name}' importado con éxito.")
                except Exception as e:
                    logger.error(f"Error importando '{import_path}': {e}")

        _LOADED = True

def get_available_llms() -> dict:
    """
    Retorna el diccionario con los adaptadores de LLMs disponibles.
    Si aún no se han cargado, los carga automáticamente.
    """
    if not _LOADED:
        load_llms_adapters()
    return LLM_REGISTRY
