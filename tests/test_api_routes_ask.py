"""
tests/test_api_routes_ask.py – Pruebas del endpoint /ask

Este test utiliza FastAPI TestClient para simular solicitudes al endpoint /ask.
Se simulan casos de éxito y error, utilizando mocks para reemplazar la funcionalidad
del pipeline RAG.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import os

# Para evitar que se cargue el .env del proyecto en estos tests,
# forzamos que la configuración no use un archivo de entorno.
os.environ["PYDANTIC_SETTINGS__ENV_FILE"] = ""

# Importar la aplicación FastAPI
from api.app import app

client = TestClient(app)

# Dummy pipeline para simular la generación de respuesta
class DummyRAGPipeline:
    def run(self, query: str, project_path: str = None) -> str:
        return f"Respuesta simulada para: {query}"

# Parcheamos la clase RAGPipeline en el módulo core.pipeline para forzar su sustitución
@pytest.fixture(autouse=True)
def patch_pipeline():
    with patch("core.pipeline.RAGPipeline", return_value=DummyRAGPipeline()) as mock_pipeline:
        yield mock_pipeline

def test_ask_endpoint_success():
    # Configuramos una API key dummy para evitar errores en adaptadores
    # (aunque el dummy pipeline no la utilice)
    import os
    os.environ["OPENAI_API_KEY"] = "dummy_api_key"
    
    # Simular una solicitud POST con un payload válido
    payload = {"query": "Hola, ¿qué tal?"}
    response = client.post("/ask/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Verificamos que la respuesta contenga la respuesta simulada
    assert "Respuesta simulada para: Hola, ¿qué tal?" in data.get("response", "")

def test_ask_endpoint_invalid_payload():
    payload = {"text": "Hola"}  # No tiene el campo "query"
    response = client.post("/ask/", json=payload)
    # Se espera un error 422 (Unprocessable Entity)
    assert response.status_code == 422

def test_ask_endpoint_pipeline_error(monkeypatch):
    # Simular que el pipeline lanza un error al ejecutar run()
    def dummy_run(query, project_path=None):
        raise Exception("Error en el pipeline")
    with patch("core.pipeline.RAGPipeline", return_value=MagicMock(run=dummy_run)):
        payload = {"query": "Hola"}
        response = client.post("/ask/", json=payload)
        # Se espera error 500 con mensaje genérico
        assert response.status_code == 500
        data = response.json()
        assert "Ocurrió un error interno" in data.get("detail", "")
