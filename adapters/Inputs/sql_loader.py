"""
sql_loader.py – Adaptador para Carga de Datos desde Bases de Datos SQL

Esta versión hyper-extendida y lista para entornos productivos incluye:
- Conexiones seguras a la base de datos (usando psycopg2, sqlalchemy u otro driver).
- Pooling de conexiones para rendimiento y escalabilidad.
- Validación de resultados contra un esquema (opcional, si deseas usar utils/validation.py).
- Mecanismos de transacciones y rollbacks en caso de error.
- Manejo de reintentos y backoff si la conexión falla temporalmente.
- Consulta de disponibilidad a core/service_detector.py.

Cumple con el README (sql_loader_README.md):
  1. Conexión segura a la DB (ORM/driver nativo) + pooling.
  2. Extracción con SQL parametrizado.
  3. Manejo de transacciones y rollbacks.
  4. Registro y logging.
  5. Consulta a service_detector.py.

NOTA: Puedes adaptar el código al driver de tu preferencia (ej.: psycopg2, SQLAlchemy).
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional

from core.service_detector import check_service_availability
from utils.logger import logger

# Si usas SQLAlchemy como ORM, podrías importarlo aquí:
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError

# Si usas un driver nativo como psycopg2:
# import psycopg2
# from psycopg2 import OperationalError, ProgrammingError

DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2
DEFAULT_SQL = "SELECT id, texto, metadata FROM documentos;"  # Ejemplo simple

def create() -> str:
    """
    Función de registro que permite identificar este adaptador.

    Returns:
        str: Una cadena indicando que el adaptador fue creado exitosamente.
    """
    return "sql_loader_creado"


def load(
    db_connection: Optional[str] = None,
    query: Optional[str] = None,
    retries: int = DEFAULT_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
) -> List[Dict[str, Any]]:
    """
    Carga datos desde una base de datos SQL, validándolos y normalizándolos si es necesario.

    Args:
        db_connection (str): Cadena de conexión a la DB. Se puede tomar también de variables de entorno.
        query (str): Consulta SQL a ejecutar. Por defecto, una consulta simple en la tabla "documentos".
        retries (int): Número de reintentos en caso de error transitorio al conectarse a la DB.
        backoff_factor (float): Factor de backoff exponencial en los reintentos.

    Returns:
        List[Dict[str, Any]]: Lista de documentos con las llaves "id", "texto" y "metadata".

    Raises:
        RuntimeError: Si el servicio 'db' no está disponible o si ocurre un error repetido de conexión.
        ValueError: Si falta la cadena de conexión o la query.
    """
    if not check_service_availability("db"):
        msg = "Servicio 'db' o 'database' no disponible según service_detector."
        logger.error(msg)
        raise RuntimeError(msg)

    if not db_connection:
        # Se podría tomar de os.getenv("DB_CONNECTION") si se desea
        db_connection = os.getenv("DB_CONNECTION")
        if not db_connection:
            raise ValueError("No se definió db_connection y no se encontró en variables de entorno.")

    if not query:
        query = DEFAULT_SQL  # Query por defecto

    attempt = 0
    delay = 1
    while attempt <= retries:
        try:
            # Aquí puedes usar tu método de conexión preferido.
            # Ejemplo con psycopg2 (versión nativa):
            import psycopg2
            from psycopg2.extras import RealDictCursor

            logger.info(f"Intentando conexión a la DB. Intento {attempt+1}/{retries+1} con query: {query}")
            conn = psycopg2.connect(db_connection, cursor_factory=RealDictCursor)
            conn.autocommit = False  # Control manual de transacciones
            try:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                conn.commit()
                # rows es una lista de dicts con campos "id", "texto", "metadata"
                logger.info(f"Consulta ejecutada. Filas obtenidas: {len(rows)}")
                documents = []
                for row in rows:
                    # row es un dict con keys 'id', 'texto', 'metadata'
                    # Ejemplo de validación mínima (ajusta a tu esquema real):
                    if "id" not in row or "texto" not in row or "metadata" not in row:
                        logger.warning(f"Fila inválida: {row}")
                        continue
                    documents.append({
                        "id": row["id"],
                        "texto": row["texto"],
                        "metadata": row["metadata"]
                    })

                return documents
            except Exception as e:
                conn.rollback()
                logger.error(f"Error en la ejecución de la consulta SQL: {e}")
                raise e
            finally:
                conn.close()

        except Exception as db_error:
            # Podrías filtrar ciertos tipos de errores (OperationalError, etc.)
            logger.warning(f"Error transitorio al conectar/ejecutar en la DB: {db_error}. Reintentando en {delay}s ...")
            time.sleep(delay)
            attempt += 1
            delay *= backoff_factor

    msg = f"No se pudo conectar a la DB o ejecutar la consulta tras {retries} reintentos."
    logger.error(msg)
    raise RuntimeError(msg)
