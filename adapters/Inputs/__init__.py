"""
__init__.py (Inputs) – Registro Dinámico y Extremo de Adaptadores de Carga de Datos

Objetivos:
  - Explorar los archivos .py en la carpeta actual (excepto __init__.py, _prefijo oculto).
  - Importar dichos módulos, detectando si tienen métodos relevantes como load() o create().
  - Mantener un diccionario global INPUTS_REGISTRY con la referencia a cada adaptador (p. ej. "json_loader": <module>).
  - Permitir un control thread-safe (para entornos multihilo).
  - Integrarse con loader.py, service_detector.py o pipeline para inyectar adaptadores.

Características Avanzadas:
  - Parámetro force_reload para recargar si se han añadido o modificado adaptadores en tiempo de ejecución.
  - Bloqueo con threading.Lock para evitar condiciones de carrera en cargas simultáneas.
  - Logs detallados para diagnosticar problemas de importación.

Uso Principal:
  - Llamar load_inputs_adapters() en la fase de inicialización si no se quiere autocarga.
  - get_available_inputs() para obtener el registro y así acceder a un módulo concreto (por nombre).
"""

import os
import logging
import importlib
import threading

logger = logging.getLogger("InputsInitLogger")
logger.setLevel(logging.DEBUG)

_INPUTS_LOCK = threading.Lock()
INPUTS_REGISTRY = {}  # { "json_loader": module, "sql_loader": module, ... }
_LOADED = False

def load_inputs_adapters(force_reload: bool = False) -> None:
    """
    Escanea el directorio (adapters/Inputs) y carga cada módulo .py.
    Excluye __init__.py y archivos con prefijo "_".
    Registra en INPUTS_REGISTRY con la clave = nombre del archivo (sin .py).

    Args:
        force_reload (bool): Si True, limpia el registro y fuerza un nuevo escaneo.
    """
    global _LOADED, INPUTS_REGISTRY

    with _INPUTS_LOCK:
        if _LOADED and not force_reload:
            logger.debug("Adaptadores de Inputs ya se encuentran cargados; no se realiza recarga.")
            return

        INPUTS_REGISTRY.clear()
        current_dir = os.path.dirname(__file__)
        logger.info(f"Descubriendo adaptadores de Inputs en: {current_dir}")

        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and filename != "__init__.py" and not filename.startswith("_"):
                module_name = filename[:-3]  # remove .py
                import_path = f"adapters.Inputs.{module_name}"
                try:
                    mod = importlib.import_module(import_path)
                    INPUTS_REGISTRY[module_name] = mod
                    logger.info(f"Módulo de Inputs '{module_name}' importado con éxito.")
                except Exception as e:
                    logger.error(f"Error al importar '{import_path}': {e}")

        _LOADED = True

def get_available_inputs() -> dict:
    """
    Retorna el diccionario con los adaptadores de Inputs disponibles.
    Si no se han cargado aún, se hace la carga por defecto.
    """
    if not _LOADED:
        load_inputs_adapters()
    return INPUTS_REGISTRY
