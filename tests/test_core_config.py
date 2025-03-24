import pytest
from pathlib import Path
from core.config import Config, get_config, update_config

def test_config_loading_from_env(tmp_path: Path, monkeypatch):
    # Crea un archivo .env temporal con las claves en minúsculas
    env_content = "\n".join([
        "openai_api_key=test_api_key",
        "db_connection=postgresql://user:pass@localhost:5432/testdb"
    ])
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    # Establece las variables necesarias en el entorno (todo en minúsculas)
    monkeypatch.setenv("openai_api_key", "test_api_key")
    monkeypatch.setenv("db_connection", "postgresql://user:pass@localhost:5432/testdb")
    monkeypatch.setenv("input", "json_loader")
    monkeypatch.setenv("embedder", "openai_embedder")
    monkeypatch.setenv("vector_store", "faiss_store")
    monkeypatch.setenv("llm", "openai_generator")
    monkeypatch.setenv("search_k", "10")

    # Inicializa la configuración desde el archivo .env temporal
    # Se pasa el path del .env temporal para forzar la lectura
    config = Config(_env_file=str(env_file))
    assert config.api_key == "test_api_key"
    assert config.db_connection == "postgresql://user:pass@localhost:5432/testdb"
    assert config.search_k == 10

def test_get_config_singleton(monkeypatch):
    # Establece las variables de entorno (en minúsculas)
    monkeypatch.setenv("openai_api_key", "key1")
    monkeypatch.setenv("db_connection", "conn1")
    monkeypatch.setenv("input", "json_loader")
    monkeypatch.setenv("embedder", "openai_embedder")
    monkeypatch.setenv("vector_store", "faiss_store")
    monkeypatch.setenv("llm", "openai_generator")
    monkeypatch.setenv("search_k", "5")

    config1 = get_config()
    config2 = get_config()
    # Se debe obtener la misma instancia
    assert config1 is config2
    assert config1.api_key == "key1"

def test_update_config(monkeypatch):
    # Inicializa variables de entorno básicas (en minúsculas)
    monkeypatch.setenv("openai_api_key", "key1")
    monkeypatch.setenv("db_connection", "conn1")
    monkeypatch.setenv("input", "json_loader")
    monkeypatch.setenv("embedder", "openai_embedder")
    monkeypatch.setenv("vector_store", "faiss_store")
    monkeypatch.setenv("llm", "openai_generator")
    monkeypatch.setenv("search_k", "5")

    config = get_config()
    assert config.search_k == 5
    # Actualiza la configuración
    update_config({"search_k": 7, "api_key": "key2"})
    config_updated = get_config()
    assert config_updated.search_k == 7
    assert config_updated.api_key == "key2"
