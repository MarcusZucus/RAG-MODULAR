"""
test_utils_validation.py – Pruebas para el módulo utils/validation.py

Cobertura:
  1. Carga de esquemas y uso de la caché.
  2. Validación exitosa de documentos.
  3. Manejo de errores (archivo de esquema inexistente, JSON no válido, documento inválido).
  4. Uso de schema dict directo vs. schema_path.
  5. Limpieza de la caché de esquemas.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from utils import validation
from utils.validation import ValidationError

try:
    import jsonschema
except ImportError:
    pass

@pytest.fixture
def example_schema(tmp_path):
    """
    Crea un archivo de esquema JSON temporal en disco.
    """
    schema_path = tmp_path / "test_schema.json"
    test_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "DocumentoTest",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "texto": {"type": "string", "minLength": 1},
            "metadata": {
                "type": "object",
                "properties": {
                    "origen": {"type": "string"},
                    "fecha": {"type": "string", "format": "date"}
                },
                "required": ["origen", "fecha"]
            }
        },
        "required": ["id", "texto", "metadata"]
    }
    schema_path.write_text(json.dumps(test_schema), encoding="utf-8")
    return str(schema_path)

@pytest.fixture(autouse=True)
def clear_cache_fixture():
    """
    Limpia la caché de esquemas antes y después de cada test.
    """
    validation.clear_schema_cache()
    yield
    validation.clear_schema_cache()

def test_load_schema_ok(example_schema):
    # Carga exitosa del esquema
    schema = validation.load_schema(example_schema)
    assert schema["title"] == "DocumentoTest"

def test_load_schema_cache(example_schema):
    # Primero se carga sin caché
    schema1 = validation.load_schema(example_schema)
    # Forzamos la recarga y verificamos que devuelva el mismo objeto (por la caché)
    schema2 = validation.load_schema(example_schema)
    assert schema1 is schema2  # Debe ser el mismo dict en memoria

def test_load_schema_non_existent(tmp_path):
    schema_path = str(tmp_path / "no_existe.json")
    with pytest.raises(FileNotFoundError, match="No se encontró el archivo de esquema"):
        validation.load_schema(schema_path)

def test_load_schema_invalid_json(tmp_path):
    invalid_file = tmp_path / "invalid_schema.json"
    invalid_file.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        validation.load_schema(str(invalid_file))

def test_validate_document_ok(example_schema):
    doc = {
        "id": "doc1",
        "texto": "Texto de prueba",
        "metadata": {"origen": "ejemplo", "fecha": "2025-03-22"}
    }
    assert validation.validate_document(doc, schema_path=example_schema) is True

def test_validate_document_missing_required(example_schema):
    doc_incompleto = {
        "id": "doc2",
        "metadata": {"origen": "falta_texto", "fecha": "2025-01-01"}
    }
    with pytest.raises(ValidationError, match="Documento inválido: .*texto.* is a required property"):
        validation.validate_document(doc_incompleto, schema_path=example_schema)

def test_validate_document_direct_schema():
    # Si se pasa el schema directamente, no es necesario schema_path
    schema = {
        "type": "object",
        "properties": {"x": {"type": "number"}},
        "required": ["x"]
    }
    good_doc = {"x": 123}
    assert validation.validate_document(good_doc, schema=schema)

def test_validate_document_no_schema():
    doc = {"algo": "valor"}
    with pytest.raises(ValueError, match="schema.* o un 'schema_path'"):
        validation.validate_document(doc)

def test_validate_document_no_jsonschema(monkeypatch):
    # Simulamos que no se ha importado jsonschema
    monkeypatch.delitem(globals(), "jsonschema", raising=False)
    with pytest.raises(ValidationError, match="La librería 'jsonschema' no está disponible"):
        validation.validate_document({"a": 1}, schema={"type": "object"})
