"""
tests/test_plugins_discovery.py – Pruebas para el módulo plugins/discovery.py

Este test cubre:
  1. Escaneo exitoso en una estructura de directorios simulada.
  2. Manejo de errores cuando el directorio no existe.
  3. Verificación de metadatos básicos (opcional).
  4. Uso de la caché y su limpieza.

Cumple con lo descrito en discovery_README.md.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from plugins import discovery

@pytest.fixture
def fake_adapters_structure(tmp_path: Path):
    """
    Crea una estructura temporal simulando la carpeta 'adapters' con subdirectorios y archivos .py.
       adapters/
           Embeddings/
               openai_embedder.py
           LLMs/
               openai_generator.py
               local_llm_generator.py
           VectorStores/
               faiss_store.py
               __init__.py  # simular archivo init
    """
    adapters_dir = tmp_path / "adapters"
    embeddings_dir = adapters_dir / "Embeddings"
    llms_dir = adapters_dir / "LLMs"
    vs_dir = adapters_dir / "VectorStores"

    # Crear subcarpetas
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    llms_dir.mkdir(parents=True, exist_ok=True)
    vs_dir.mkdir(parents=True, exist_ok=True)

    # Crear archivos .py
    (embeddings_dir / "openai_embedder.py").write_text("# openai_embedder code")
    (llms_dir / "openai_generator.py").write_text("# openai_generator code")
    (llms_dir / "local_llm_generator.py").write_text("# local_llm_generator code")
    (vs_dir / "faiss_store.py").write_text("# faiss_store code")
    (vs_dir / "__init__.py").write_text("")  # init file

    return adapters_dir

def test_discover_plugins_success(fake_adapters_structure):
    """
    Prueba un escaneo exitoso en un árbol simulado.
    """
    result = discovery.discover_plugins(str(fake_adapters_structure))
    assert len(result["errors"]) == 0
    # Deberíamos encontrar 4 módulos .py (exceptuando __init__.py)
    assert len(result["modules"]) == 4
    assert "Embeddings.openai_embedder" in result["modules"]
    assert "LLMs.openai_generator" in result["modules"]
    assert "LLMs.local_llm_generator" in result["modules"]
    assert "VectorStores.faiss_store" in result["modules"]

def test_discover_plugins_directory_not_exists(tmp_path):
    """
    Prueba que si el directorio no existe, se registre el error correspondiente.
    """
    non_existent_dir = tmp_path / "adapters_no_existe"
    result = discovery.discover_plugins(str(non_existent_dir))
    assert len(result["errors"]) == 1
    assert "no existe" in result["errors"][0].lower()
    assert len(result["modules"]) == 0

def test_get_discovered_plugins_cache(fake_adapters_structure):
    """
    Verifica que la cache retenga la información del último discovery.
    """
    discovery.clear_discovery_cache()
    discovery.discover_plugins(str(fake_adapters_structure))
    cache_data = discovery.get_discovered_plugins()
    assert len(cache_data["modules"]) == 4
    assert len(cache_data["errors"]) == 0

def test_clear_discovery_cache():
    """
    Valida que al limpiar la caché, se vacíen los arrays de modules y errors.
    """
    discovery._DISCOVERY_CACHE["modules"]["fake"] = {}
    discovery._DISCOVERY_CACHE["errors"].append("fake error")
    discovery.clear_discovery_cache()
    cache_data = discovery.get_discovered_plugins()
    assert len(cache_data["modules"]) == 0
    assert len(cache_data["errors"]) == 0
