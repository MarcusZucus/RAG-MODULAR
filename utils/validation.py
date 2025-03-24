"""
validation.py – Módulo de Validación de Documentos y Configuraciones

Este módulo:
  - Valida que los documentos cumplan con el esquema JSON definido (por ejemplo en data/schema_docs.json).
  - Ofrece una función genérica para cargar y validar contra distintos esquemas.
  - Lanza excepciones claras en caso de error y se integra con el logger para registrar incidencias.
  - Está diseñado para entornos de producción, admitiendo extensiones (por ejemplo, validación de configuraciones).

Cumple con validation_README.md:
  - validate_document(doc)
  - Manejo de errores con logs.
  - Normalización (opcional).
"""

import json
import os
import logging
from typing import Dict, Any, Optional

from utils.logger import logger

try:
    import jsonschema
except ImportError:
    logger.warning("No se encontró la librería 'jsonschema'. Para validaciones avanzadas, instálala con 'pip install jsonschema'")

SCHEMA_CACHE = {}

class ValidationError(Exception):
    """
    Excepción para errores de validación de documentos.
    """
    pass

def load_schema(schema_path: str) -> Dict[str, Any]:
    """
    Carga y retorna un esquema JSON desde un archivo. Almacena en caché para no recargarlo repetidamente.

    Args:
        schema_path (str): Ruta al archivo de esquema JSON.

    Returns:
        dict: El contenido del esquema JSON.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el archivo no es un JSON válido.
    """
    if schema_path in SCHEMA_CACHE:
        return SCHEMA_CACHE[schema_path]

    if not os.path.isfile(schema_path):
        raise FileNotFoundError(f"No se encontró el archivo de esquema: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_content = json.load(f)
    SCHEMA_CACHE[schema_path] = schema_content
    logger.info(f"Esquema cargado y cacheado desde: {schema_path}")
    return schema_content

def validate_document(document: Dict[str, Any],
                     schema: Optional[Dict[str, Any]] = None,
                     schema_path: Optional[str] = None) -> bool:
    """
    Valida un documento contra un esquema JSON. Se puede proporcionar directamente el schema (dict) 
    o una ruta a un archivo de esquema. En caso de error, lanza ValidationError.

    Args:
        document (dict): El documento a validar.
        schema (dict, opcional): El esquema en formato dict.
        schema_path (str, opcional): Ruta a un archivo con el esquema JSON.

    Returns:
        bool: True si la validación fue exitosa.

    Raises:
        ValidationError: Si la validación falla.
        ValueError: Si no se proporcionan ni schema ni schema_path.
    """
    if not schema and not schema_path:
        raise ValueError("Se requiere un 'schema' o un 'schema_path' para validar el documento.")

    if schema_path:
        try:
            schema = load_schema(schema_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            msg = f"Error cargando esquema desde '{schema_path}': {e}"
            logger.error(msg)
            raise ValidationError(msg)

    if not schema:
        raise ValueError("No se pudo determinar el esquema para validar.")

    # Verificar si está instalada jsonschema
    if "jsonschema" not in globals():
        msg = "La librería 'jsonschema' no está disponible. Instálala con 'pip install jsonschema'."
        logger.error(msg)
        raise ValidationError(msg)

    try:
        jsonschema.validate(instance=document, schema=schema)
        logger.debug("Documento validado correctamente.")
        return True
    except jsonschema.ValidationError as ve:
        msg = f"Documento inválido: {ve.message}"
        logger.error(msg)
        raise ValidationError(msg)

def clear_schema_cache():
    """
    Limpia la caché de esquemas. Útil para entornos de test o cuando se actualiza un esquema.
    """
    SCHEMA_CACHE.clear()
    logger.info("Cache de esquemas limpiado.")
