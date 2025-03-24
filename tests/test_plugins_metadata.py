"""
test_plugins_metadata.py – Pruebas para el módulo plugins/metadata.py

Escenarios:
  1. Validar metadatos completos y correctos.
  2. Detectar campos obligatorios faltantes.
  3. Emitir warning si faltan campos opcionales.
  4. Extraer metadatos de un módulo con __metadata__ definido.
  5. Comprobar compatibilidad con un registry simulado.

Referencia: metadata_README.md.
"""

import pytest
from unittest.mock import MagicMock

from plugins import metadata

def test_validate_metadata_complete():
    meta = {
        "name": "openai_embedder",
        "version": "1.0.0",
        "description": "Adaptador que usa OpenAI Embeddings",
        "dependencies": ["requests", "openai"],
        "requerimientos_minimos": ["python 3.9+"],
        "compatibilidades": [">=1.0.0"]
    }
    assert metadata.validate_metadata(meta) is True

def test_validate_metadata_missing_required():
    meta = {
        "name": "incompleto",
        # Falta "version" y "description"
    }
    with pytest.raises(ValueError, match="Metadatos incompletos"):
        metadata.validate_metadata(meta)

def test_validate_metadata_optional_warn(caplog):
    meta = {
        "name": "plugin_sin_opcionales",
        "version": "2.0.0",
        "description": "Faltan los opcionales"
    }
    # No debe lanzar excepción, pero sí warnings
    metadata.validate_metadata(meta)
    warns = [rec.message for rec in caplog.records if rec.levelname == "WARNING"]
    # Debe haber 3 warnings, uno para cada campo faltante en OPTIONAL_FIELDS
    assert len(warns) == 3
    assert "Campo opcional 'dependencies' no presente" in warns[0]

def test_extract_metadata_from_module():
    # Simulamos un módulo con un atributo __metadata__
    mock_module = MagicMock()
    mock_module.__name__ = "mock_module"
    mock_module.__metadata__ = {
        "name": "mock_plugin",
        "version": "0.0.1",
        "description": "Plugin de prueba"
    }
    meta = metadata.extract_metadata_from_module(mock_module)
    assert meta["name"] == "mock_plugin"

def test_extract_metadata_no_dict(caplog):
    # Simula un módulo que define __metadata__ pero no como dict
    mock_module = MagicMock()
    mock_module.__name__ = "otro_module"
    mock_module.__metadata__ = "no soy un dict"

    meta = metadata.extract_metadata_from_module(mock_module)
    assert meta == {}
    warns = [rec.message for rec in caplog.records if rec.levelname == "WARNING"]
    assert len(warns) == 1
    assert "no define un dict __metadata__" in warns[0]

def test_check_compatibility_with_registry_ok(caplog):
    meta = {
        "name": "openai_generator",
        "version": "1.2.0",
        "description": "Plugin con generador OpenAI"
    }
    registry_data = {
        "models": [
            {
                "name": "openai_generator",
                "version": "1.0.0",
                "compatibility": "1.0.0"
            }
        ]
    }
    assert metadata.check_compatibility_with_registry(meta, registry_data) is True
    # Revisa logs de info
    infos = [rec.message for rec in caplog.records if rec.levelname == "INFO"]
    assert any("es compatible con el registry" in msg for msg in infos)

def test_check_compatibility_with_registry_fail(caplog):
    meta = {
        "name": "openai_generator",
        "version": "0.9.0",  # versión menor
        "description": "Plugin con generador OpenAI"
    }
    registry_data = {
        "models": [
            {
                "name": "openai_generator",
                "version": "1.0.0",
                "compatibility": "1.0.0"
            }
        ]
    }
    result = metadata.check_compatibility_with_registry(meta, registry_data)
    assert result is False
    warns = [rec.message for rec in caplog.records if rec.levelname == "WARNING"]
    assert any("Plugin openai_generator versión 0.9.0 < 1.0.0 requerido." in msg for msg in warns)
