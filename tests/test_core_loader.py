import os
from pathlib import Path
import importlib.util
import sys
import pytest
from core.loader import load_all_adapters

@pytest.fixture
def fake_adapters(tmp_path: Path):
    """
    Crea una estructura temporal simulando la carpeta 'adapters' con subdirectorios y archivos .py.
    La estructura será:
       adapters/
           Inputs/
               json_loader.py
           Embeddings/
               openai_embedder.py
    """
    adapters_dir = tmp_path / "adapters"
    
    # Crear carpeta Inputs y un módulo json_loader.py
    inputs_dir = adapters_dir / "Inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    json_loader_file = inputs_dir / "json_loader.py"
    json_loader_file.write_text(
        "def create():\n    return 'json_loader_creado'\n"
    )
    
    # Crear carpeta Embeddings y un módulo openai_embedder.py
    embeddings_dir = adapters_dir / "Embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    openai_embedder_file = embeddings_dir / "openai_embedder.py"
    openai_embedder_file.write_text(
        "def create():\n    return 'openai_embedder_creado'\n"
    )
    
    # Agregar __init__.py vacíos en cada directorio para que sean paquetes
    for d in [adapters_dir, inputs_dir, embeddings_dir]:
        init_file = d / "__init__.py"
        init_file.write_text("")
    
    return adapters_dir

def test_loader_discovers_modules(fake_adapters: Path, monkeypatch):
    # Agregamos el directorio temporal al sys.path para que se puedan importar los módulos
    monkeypatch.syspath_prepend(str(fake_adapters.parent))
    
    # Llamamos a la función de carga de adaptadores apuntando al directorio temporal
    adapters = load_all_adapters(root_dir=str(fake_adapters))
    
    # Verificamos que se descubren las categorías Inputs y Embeddings
    assert "Inputs" in adapters, "No se encontró la categoría 'Inputs'"
    assert "Embeddings" in adapters, "No se encontró la categoría 'Embeddings'"
    
    # Verificamos que se haya descubierto el módulo json_loader en Inputs
    inputs_modules = adapters["Inputs"]
    assert "json_loader" in inputs_modules, "No se encontró el módulo 'json_loader' en Inputs"
    # Comprobamos que la función create retorna el valor esperado
    json_loader_module = inputs_modules["json_loader"]
    assert json_loader_module.create() == "json_loader_creado"
    
    # Verificamos el módulo openai_embedder en Embeddings
    embeddings_modules = adapters["Embeddings"]
    assert "openai_embedder" in embeddings_modules, "No se encontró el módulo 'openai_embedder' en Embeddings"
    openai_module = embeddings_modules["openai_embedder"]
    assert openai_module.create() == "openai_embedder_creado"
