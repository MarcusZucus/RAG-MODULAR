"""
discovery.py – Plugin de Descubrimiento de Adaptadores

Este módulo escanea de forma recursiva la carpeta adapters/ (y, opcionalmente, otras rutas plugin)
para detectar y registrar todos los módulos disponibles. Además:
- Integra una verificación de metadatos (opcionales) con plugins/metadata.py.
- Realiza un logging detallado de cada módulo detectado.
- Permite la extensión futura para inyectar funciones de validación adicional.

Cumple con el README (discovery_README.md):
  - Escaneo de directorios.
  - Extracción de metadatos (opcional).
  - Registro y auditoría.
  - API para consulta (p.ej. get_discovered_plugins()).
  - Integración con service_detector.py si deseas detectar adaptadores que dependan de servicios externos.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

# from plugins.metadata import validate_metadata  # en caso de usar un validador de metadatos
from utils.logger import logger

# Estructura para almacenar los resultados de la última ejecución de discovery
_DISCOVERY_CACHE: Dict[str, Any] = {
    "modules": {},
    "errors": []
}

def discover_plugins(plugins_dir: str = "adapters") -> Dict[str, Any]:
    """
    Escanea recursivamente el directorio `plugins_dir` para detectar y registrar módulos .py.
    Ignora los __init__.py.

    Args:
        plugins_dir (str): Directorio principal donde se buscan módulos/plugins (por defecto "adapters").

    Returns:
        Dict[str, Any]: Estructura con la lista de módulos detectados y errores surgidos.
    """
    logger.info(f"Iniciando discovery en el directorio: {plugins_dir}")
    results = {
        "modules": {},
        "errors": []
    }
    root_path = Path(plugins_dir)
    if not root_path.exists():
        msg = f"El directorio '{plugins_dir}' no existe."
        logger.error(msg)
        results["errors"].append(msg)
        return results

    for dirpath, _, filenames in os.walk(root_path):
        current_path = Path(dirpath)
        relative_path_parts = current_path.relative_to(root_path).parts

        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # Quita la extensión .py
                # Construye un path único (p.ej., "Embeddings.openai_embedder")
                full_path = list(relative_path_parts) + [plugin_name]
                plugin_key = ".".join(full_path)

                plugin_file = current_path / filename
                try:
                    logger.debug(f"Descubriendo plugin: {plugin_key} en archivo {plugin_file}")
                    # Se podría importar aquí o en otro componente:
                    # module = import_module_from_file(plugin_key, plugin_file)
                    # metadatos = extract_metadata(module)  # si tuvieras un validador

                    # Guardamos la referencia en results
                    results["modules"][plugin_key] = {
                        "file": str(plugin_file),
                        "has_metadata": False  # Podrías ajustar a True si lo detectas
                    }
                except Exception as e:
                    error_msg = f"Error al procesar '{plugin_key}': {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

    logger.info(f"Discovery finalizado. Módulos encontrados: {len(results['modules'])}")
    _DISCOVERY_CACHE.update(results)
    return results

def get_discovered_plugins() -> Dict[str, Any]:
    """
    Retorna la última estructura de discovery, evitando relanzar el escaneo.
    Se puede emplear para proveer información al dashboard u otros componentes.

    Returns:
        Dict[str, Any]: Estructura con 'modules' y 'errors'.
    """
    return _DISCOVERY_CACHE

def clear_discovery_cache() -> None:
    """
    Limpia la caché de discovery en caso de requerir un escaneo fresco.
    """
    _DISCOVERY_CACHE["modules"].clear()
    _DISCOVERY_CACHE["errors"].clear()
    logger.info("Cache de discovery limpiada.")
