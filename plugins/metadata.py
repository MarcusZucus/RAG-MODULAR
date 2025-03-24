"""
metadata.py – Módulo para Validación y Gestión de Metadatos de Plugins/Adaptadores

Este módulo:
  - Define un esquema de metadatos que cada plugin o adaptador puede (opcionalmente) implementar.
  - Provee funciones para validar que el plugin cumpla con ciertos campos obligatorios, versiones y dependencias.
  - Permite la extensión para auditar compatibilidad e integrarse con un registro (model_registry.json).

Guía metadata_README.md:
  - Definición del esquema y funciones de validación.
  - Integración con discovery (opcional).
  - Registro y manejo de advertencias/errores.

Versión state-of-the-art:
  - Usa un validador interno e integra logging para advertir o bloquear si no cumple metadatos básicos.
  - Se puede conectar con `discovery.py` para leer metadatos en cada plugin detectado.
"""

import logging
from typing import Dict, Any

from utils.logger import logger

# Ejemplo de esquema mínimo que un plugin podría definir, ajusta a tus necesidades:
REQUIRED_FIELDS = ["name", "version", "description"]
OPTIONAL_FIELDS = ["dependencies", "requerimientos_minimos", "compatibilidades"]

def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Valida que los metadatos del plugin cuenten con los campos mínimos requeridos.
    Opcionalmente, se revisan campos opcionales y se registran advertencias si faltan.

    Args:
        metadata (dict): Diccionario con metadatos del plugin. 
                         Se espera que incluya "name", "version", "description", 
                         y opcionalmente "dependencies", "requerimientos_minimos", "compatibilidades".

    Returns:
        bool: True si los metadatos cumplen el esquema mínimo, False si falta algo crucial.

    Raises:
        ValueError: Si detecta que no hay un campo esencial (por ejemplo, "name").
                    Dependiendo de tu preferencia, se podría usar un return False en vez de exception.
    """
    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        msg = f"Metadatos incompletos, faltan campos esenciales: {missing}"
        logger.error(msg)
        raise ValueError(msg)

    # Verificamos los campos opcionales; no son imprescindibles, pero podemos advertir:
    for field in OPTIONAL_FIELDS:
        if field not in metadata:
            logger.warning(f"Campo opcional '{field}' no presente en metadatos de '{metadata.get('name','desconocido')}'.")

    logger.info(f"Metadatos validados para plugin '{metadata['name']}' – versión {metadata['version']}.")
    return True

def extract_metadata_from_module(module) -> Dict[str, Any]:
    """
    Extrae metadatos de un objeto módulo (opcionalmente, de una variable __metadata__).
    Se asume que, si el módulo define algo como:
       __metadata__ = {
         "name": "openai_embedder",
         "version": "1.0.0",
         "description": "Adaptador que usa OpenAI Embeddings"
       }
    se devuelva ese dict. Si no, retorna un dict vacío.

    Args:
        module: Módulo de Python donde se busca la variable __metadata__.

    Returns:
        dict: Metadatos extraídos o un dict vacío.
    """
    meta = getattr(module, "__metadata__", {})
    if not isinstance(meta, dict):
        logger.warning(f"El módulo {module.__name__} no define un dict __metadata__, se ignora.")
        return {}
    return meta

def check_compatibility_with_registry(metadata: Dict[str, Any], registry_data: Dict[str, Any]) -> bool:
    """
    Comprueba (de forma opcional/extendida) si el plugin es compatible con la información
    presente en model_registry.json (por ejemplo, versiones mínimas, dependencias).

    Args:
        metadata (dict): Metadatos validados del plugin.
        registry_data (dict): Datos del registry (normalmente cargado de model_registry.json).

    Returns:
        bool: True si cumple con la compatibilidad indicada, False en caso contrario.
    """
    plugin_name = metadata.get("name", "")
    plugin_version = metadata.get("version", "")
    # Ejemplo simplificado: se busca plugin_name en registry_data["models"] y se comparan versiones
    model_entries = registry_data.get("models", [])
    for entry in model_entries:
        if entry.get("name", "") == plugin_name:
            required_compat = entry.get("compatibility", "")
            # Lógica simplificada; en un caso real, se parsea la version con semver.
            if required_compat and plugin_version < required_compat:
                logger.warning(f"Plugin {plugin_name} versión {plugin_version} < {required_compat} requerido.")
                return False
    logger.info(f"Plugin {plugin_name} versión {plugin_version} es compatible con el registry.")
    return True
