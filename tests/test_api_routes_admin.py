# tests/test_api_routes_admin.py

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.app import app

client = TestClient(app)

def test_admin_get_logs(monkeypatch):
    mock_logs = [
        {"timestamp": 123.45, "level": "info", "message": "Log1", "module": "test"},
        {"timestamp": 678.90, "level": "error", "message": "Log2", "module": "test"}
    ]
    def mock_get_logs(level=None):
        if level:
            return [l for l in mock_logs if l["level"] == level]
        return mock_logs

    monkeypatch.setattr("api.routes.admin.get_logs", mock_get_logs)
    resp = client.get("/admin/logs?level=error")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert len(data["logs"]) == 1
    assert data["logs"][0]["message"] == "Log2"

def test_admin_get_metrics(monkeypatch):
    mock_metrics = [
        {"timestamp": 111.11, "name": "response_time", "value": 300},
        {"timestamp": 222.22, "name": "cpu_usage", "value": 50}
    ]
    def mock_get_metrics(name=None):
        if name:
            return [m for m in mock_metrics if m["name"] == name]
        return mock_metrics

    monkeypatch.setattr("api.routes.admin.get_metrics", mock_get_metrics)
    resp = client.get("/admin/metrics?name=cpu_usage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["metrics"][0]["name"] == "cpu_usage"

def test_admin_update_config(monkeypatch):
    def mock_update_config(changes: dict):
        # Simular que la config se actualiza sin problema
        pass
    def mock_get_config():
        class FakeConfig:
            def model_dump(self):
                return {"search_k": 10, "openai_api_key": "dummy_key"}
        return FakeConfig()

    monkeypatch.setattr("api.routes.admin.update_config", mock_update_config)
    monkeypatch.setattr("api.routes.admin.get_config", mock_get_config)

    payload = {"search_k": 10, "api_key": "nueva_api"}
    resp = client.post("/admin/config", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Configuración actualizada" in data["message"]
    assert data["new_config"]["search_k"] == 10

def test_admin_update_config_no_changes():
    resp = client.post("/admin/config", json={})
    assert resp.status_code == 400
    data = resp.json()
    assert "No hay cambios" in data["detail"]

def test_admin_system_reset(monkeypatch):
    def mock_clear_data():
        pass
    def mock_clear_schema_cache():
        pass

    monkeypatch.setattr("api.routes.admin.clear_data", mock_clear_data)
    monkeypatch.setattr("api.routes.admin.clear_schema_cache", mock_clear_schema_cache)

    resp = client.post("/admin/reset?full_reset=true")
    data = resp.json()
    assert resp.status_code == 200
    assert "FULL RESET completado" in data["message"]
