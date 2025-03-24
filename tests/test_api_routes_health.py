# tests/test_api_routes_health.py

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.app import app

client = TestClient(app)

@pytest.fixture
def mock_config_env():
    """
    Cambia variables de entorno o la configuración global si se requiere.
    """
    # Podrías usar monkeypatch o un approach similar
    pass

def test_health_all_up(monkeypatch):
    """
    Escenario: Todos los servicios están disponibles -> overall_status = UP.
    """
    def mock_check(service):
        return True  # Fuerza que todos devuelvan True
    monkeypatch.setattr("api.routes.health.check_service_availability", mock_check)

    # Simular adaptadores críticos en config
    def mock_get_config():
        class FakeConfig:
            input = "json_loader"
            embedder = "openai_embedder"
            vector_store = "faiss_store"
            llm = "openai_generator"
        return FakeConfig()
    monkeypatch.setattr("api.routes.health.get_config", mock_get_config)

    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "UP"
    # Verifica que cada chequeo esté en UP
    for check in data["checks"]:
        assert check["status"] == "UP"

def test_health_db_down(monkeypatch):
    """
    Escenario: DB no disponible, pero OpenAI sí -> overall: DEGRADED
    """
    def mock_check(service):
        if service == "db":
            return False
        return True
    monkeypatch.setattr("api.routes.health.check_service_availability", mock_check)

    def mock_get_config():
        class FakeConfig:
            input = "json_loader"
            embedder = "openai_embedder"
            vector_store = "faiss_store"
            llm = "openai_generator"
        return FakeConfig()
    monkeypatch.setattr("api.routes.health.get_config", mock_get_config)

    resp = client.get("/health/")
    data = resp.json()
    assert resp.status_code == 200
    assert data["overall_status"] == "DEGRADED"
    db_check = next((c for c in data["checks"] if c["service"] == "database"), None)
    assert db_check is not None
    assert db_check["status"] == "DOWN"

def test_health_all_down(monkeypatch):
    """
    Escenario: DB y OpenAI no disponibles -> overall = DOWN
    """
    def mock_check(service):
        return False
    monkeypatch.setattr("api.routes.health.check_service_availability", mock_check)

    def mock_get_config():
        class FakeConfig:
            input = None
            embedder = None
            vector_store = None
            llm = None
        return FakeConfig()
    monkeypatch.setattr("api.routes.health.get_config", mock_get_config)

    resp = client.get("/health/")
    data = resp.json()
    assert resp.status_code == 200
    assert data["overall_status"] == "DOWN"
    # Verificar que “database” y “openai_api” estén en DOWN
    db_check = next(c for c in data["checks"] if c["service"] == "database")
    openai_check = next(c for c in data["checks"] if c["service"] == "openai_api")
    assert db_check["status"] == "DOWN"
    assert openai_check["status"] == "DOWN"
