"""
tests/test_adapters_inputs_api_loader.py – Pruebas para el adaptador adapters/Inputs/api_loader.py

Este test cubre:
  1. Llamada exitosa con datos JSON válidos.
  2. Llamada fallida (códigos de error HTTP).
  3. Reintentos con backoff y simulación de fallo transitorio.
  4. Validación de parámetros obligatorios (URL).
  5. Manejo de token de autenticación.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from adapters.Inputs import api_loader
from requests.exceptions import ConnectionError, Timeout

@pytest.fixture
def mock_check_service(monkeypatch):
    """
    Fuerza check_service_availability("api_loader") a True para simular que el servicio está disponible.
    """
    def dummy_check(_):
        return True
    monkeypatch.setattr("adapters.Inputs.api_loader.check_service_availability", dummy_check)


def test_create_api_loader():
    assert api_loader.create() == "api_loader_creado"


def test_load_successful(mock_check_service, monkeypatch):
    # Simulamos la respuesta de requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "doc1", "texto": "Texto de ejemplo", "metadata": {"origen": "api", "fecha": "2025-01-01"}},
        {"id": "doc2", "texto": "Otro texto", "metadata": {"origen": "api", "fecha": "2025-01-02"}}
    ]

    def mock_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)
    
    docs = api_loader.load(url="http://fakeapi.com/docs")
    assert len(docs) == 2
    assert docs[0]["id"] == "doc1"


def test_load_http_error(mock_check_service, monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    
    def mock_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(RuntimeError, match="Error HTTP 404: Not Found"):
        api_loader.load(url="http://fakeapi.com/docs")


def test_load_transient_failure_retry(mock_check_service, monkeypatch):
    """
    Simula un fallo de conexión transitorio en el primer intento y éxito en el segundo.
    """
    call_count = {"count": 0}
    
    def mock_get(*args, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise ConnectionError("Fallo de conexión simulado")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "doc1", "texto": "Texto", "metadata": {"origen": "api", "fecha": "2025-03-01"}}]
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)
    
    docs = api_loader.load(url="http://fakeapi.com/docs", retries=2, backoff_factor=1)
    assert len(docs) == 1
    assert call_count["count"] == 1  # Verificar que realmente hubo un reintento


def test_load_missing_url(mock_check_service):
    """
    Verifica que se lance ValueError si no se pasa URL.
    """
    with pytest.raises(ValueError, match="Se requiere una URL"):
        api_loader.load(url=None)


def test_load_with_auth_token(mock_check_service, monkeypatch):
    """
    Verifica que se incluya el Bearer token en headers si auth_token está presente.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    def mock_get(*args, **kwargs):
        headers = kwargs.get("headers", {})
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer secret_token"
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)
    
    docs = api_loader.load(url="http://fakeapi.com/protected", auth_token="secret_token")
    assert isinstance(docs, list)
    assert len(docs) == 0
