import os
import json
import pytest
from pathlib import Path
from core.service_detector import check_service_availability

# Fixture para guardar y restaurar el directorio de trabajo original
@pytest.fixture
def original_cwd():
    cwd = os.getcwd()
    yield cwd
    os.chdir(cwd)

# Test para servicios OpenAI: sin API key
def test_openai_service_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert not check_service_availability("openai")

# Test para servicios OpenAI: con API key
def test_openai_service_with_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    assert check_service_availability("openai_generator")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

# Test para modelo gguf: sin variable
def test_gguf_service_without_env(monkeypatch):
    monkeypatch.delenv("GGUF_MODEL_PATH", raising=False)
    assert not check_service_availability("gguf")

# Test para modelo gguf: variable con ruta inválida
def test_gguf_service_with_invalid_path(monkeypatch):
    monkeypatch.setenv("GGUF_MODEL_PATH", "ruta_invalida/model.gguf")
    assert not check_service_availability("local_llm_generator")
    monkeypatch.delenv("GGUF_MODEL_PATH", raising=False)

# Test para modelo gguf: variable con ruta válida usando tmp_path
def test_gguf_service_with_valid_path(monkeypatch, tmp_path):
    model_file = tmp_path / "model.gguf"
    model_file.write_text("dummy content")
    monkeypatch.setenv("GGUF_MODEL_PATH", str(model_file))
    assert check_service_availability("gguf")
    monkeypatch.delenv("GGUF_MODEL_PATH", raising=False)

# Test para pre_rag: sin directorio 'pre_rag'
def test_pre_rag_service_without_directory(monkeypatch, tmp_path, original_cwd):
    # Cambia el directorio de trabajo al temporal y no crea 'pre_rag'
    os.chdir(tmp_path)
    assert not check_service_availability("pre_rag")

# Test para pre_rag: directorio 'pre_rag' creado pero sin archivos JSON
def test_pre_rag_service_without_json(monkeypatch, tmp_path, original_cwd):
    os.chdir(tmp_path)
    pre_rag_dir = tmp_path / "pre_rag"
    pre_rag_dir.mkdir()
    assert not check_service_availability("pre_rag")

# Test para pre_rag: directorio 'pre_rag' con al menos un archivo JSON
def test_pre_rag_service_with_json(monkeypatch, tmp_path, original_cwd):
    os.chdir(tmp_path)
    pre_rag_dir = tmp_path / "pre_rag"
    pre_rag_dir.mkdir()
    json_file = pre_rag_dir / "vagon1.json"
    json_file.write_text(json.dumps({"key": "value"}))
    assert check_service_availability("pre_rag")

# Test para base de datos: sin variable de conexión
def test_db_service_without_connection(monkeypatch):
    monkeypatch.delenv("DB_CONNECTION", raising=False)
    assert not check_service_availability("db")

# Test para base de datos: con variable de conexión
def test_db_service_with_connection(monkeypatch):
    monkeypatch.setenv("DB_CONNECTION", "postgresql://user:pass@localhost:5432/testdb")
    assert check_service_availability("database")
    monkeypatch.delenv("DB_CONNECTION", raising=False)

# Test para un servicio no definido explícitamente: se asume disponibilidad
def test_default_service(monkeypatch):
    assert check_service_availability("servicio_no_definido")
