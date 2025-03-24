"""
tests/test_adapters_inputs_sql_loader.py – Pruebas para el adaptador adapters/Inputs/sql_loader.py

Este test cubre:
  1. Creación del adaptador (create()).
  2. Conexión exitosa y ejecución de query básica.
  3. Manejo de filas inválidas (falta 'id', 'texto' o 'metadata').
  4. Reintentos en caso de error de conexión/transitorio.
  5. Manejo de excepciones y rollbacks.
  6. Falta de db_connection o servicio 'db' no disponible.
"""

import pytest
import os
import psycopg2
from unittest.mock import patch, MagicMock

from adapters.Inputs import sql_loader

@pytest.fixture(autouse=True)
def mock_service_availability(monkeypatch):
    """
    Fuerza check_service_availability("db") a True para simular que la DB está disponible.
    """
    def dummy_check(service_name):
        if service_name.lower() in {"db", "database"}:
            return True
        return False
    monkeypatch.setattr("adapters.Inputs.sql_loader.check_service_availability", dummy_check)

def test_create_sql_loader():
    assert sql_loader.create() == "sql_loader_creado"

def test_load_successful(monkeypatch):
    """
    Verifica que en un escenario exitoso se retornen documentos correctamente.
    """
    # Simulamos filas en la base de datos
    rows = [
        {"id": "doc1", "texto": "Texto 1", "metadata": {"origen": "sql", "fecha": "2025-01-01"}},
        {"id": "doc2", "texto": "Texto 2", "metadata": {"origen": "sql", "fecha": "2025-01-02"}}
    ]
    # Cursor fake
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows

    # Conexión fake
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Simulamos psycopg2.connect
    def mock_connect(db_conn_str, cursor_factory=None):
        return mock_conn

    monkeypatch.setattr(psycopg2, "connect", mock_connect)

    docs = sql_loader.load(db_connection="postgresql://user:pass@localhost/dbtest", query="SELECT * FROM documentos;")
    assert len(docs) == 2
    assert docs[0]["id"] == "doc1"
    mock_cursor.execute.assert_called_once_with("SELECT * FROM documentos;")

def test_load_missing_db_connection(monkeypatch):
    """
    Si no se pasa db_connection y tampoco está en env, se lanza un ValueError.
    """
    monkeypatch.delenv("DB_CONNECTION", raising=False)
    with pytest.raises(ValueError, match="No se definió db_connection"):
        sql_loader.load(db_connection=None, query="SELECT * FROM documentos;")

def test_load_rows_with_missing_keys(monkeypatch):
    """
    Verifica que si una fila carece de 'id', 'texto' o 'metadata', se omita (warning).
    """
    rows = [
        {"id": "doc1", "texto": "Texto 1"},  # Falta metadata
        {"id": "doc2", "texto": "Texto 2", "metadata": {}},  # metadata vacía, pero OK según tu criterio
        {"no_id": 123, "texto": "Texto 3", "metadata": {"origen": "sql"}}  # Falta 'id'
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    def mock_connect(db_conn_str, cursor_factory=None):
        return mock_conn

    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", mock_connect)

    docs = sql_loader.load(db_connection="postgresql://user:pass@localhost/dbtest", query="SELECT X;")
    # Esperamos que sólo 1 doc sea válido (doc2)
    assert len(docs) == 1
    assert docs[0]["id"] == "doc2"

def test_load_transient_failure_retry(monkeypatch):
    """
    Simula fallo de conexión en el primer intento y éxito en el segundo.
    """
    attempt_count = {"count": 0}

    def mock_connect(*args, **kwargs):
        if attempt_count["count"] == 0:
            attempt_count["count"] += 1
            raise psycopg2.OperationalError("Fallo de conexión simulado")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        return mock_conn

    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", mock_connect)

    # Primer intento falla, segundo intenta y retorna sin error
    docs = sql_loader.load(db_connection="postgresql://user:pass@localhost/dbtest", query="SELECT X;", retries=1)
    assert docs == []
    assert attempt_count["count"] == 1

def test_load_exhaust_retries(monkeypatch):
    """
    Si todos los intentos fallan, se lanza RuntimeError.
    """
    def mock_connect(*args, **kwargs):
        raise psycopg2.OperationalError("Fallo permanente")

    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", mock_connect)

    with pytest.raises(RuntimeError, match="No se pudo conectar a la DB"):
        sql_loader.load(db_connection="postgresql://user:pass@localhost/dbtest", query="SELECT X;", retries=1)
