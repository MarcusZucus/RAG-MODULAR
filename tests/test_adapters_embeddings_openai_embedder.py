import os
import json
import pytest
from utils.cache_manager import _cache  # Para limpiar la caché entre tests
from adapters.Embeddings import openai_embedder

class DummyResponse:
    """Respuesta dummy simulada para openai.Embedding.create."""
    def __init__(self, embeddings):
        # Simula la estructura de respuesta de OpenAI
        self.data = [{"embedding": emb} for emb in embeddings]

    def __getitem__(self, key):
        if key == "data":
            return self.data
        raise KeyError(key)

def dummy_embedding_create(input, model):
    """
    Función dummy para simular openai.Embedding.create.
    Retorna un embedding simple basado en la longitud del texto.
    """
    # Por cada texto, genera un vector dummy (ejemplo: [len(text)] * 5)
    embeddings = [[float(len(text))] * 5 for text in input]
    return DummyResponse(embeddings)

@pytest.fixture(autouse=True)
def clear_cache():
    # Limpiar la caché antes de cada test
    _cache.clear()
    yield
    _cache.clear()

def test_create():
    result = openai_embedder.create()
    assert result == "openai_embedder_creado"

def test_embed_success(monkeypatch):
    # Configurar la variable de entorno para la API key
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    # Reemplazar openai.Embedding.create por la función dummy
    monkeypatch.setattr(openai_embedder, "openai", type("dummy", (), {"Embedding": type("DummyEmbedding", (), {"create": dummy_embedding_create})}))
    
    texts = ["Hola", "Mundo"]
    embeddings = openai_embedder.embed(texts, model="text-embedding-ada-002", cache_ttl=3600)
    # Verificar que se generen embeddings; cada embedding es una lista de 5 elementos con el valor len(text)
    assert embeddings == [[4.0, 4.0, 4.0, 4.0, 4.0], [5.0, 5.0, 5.0, 5.0, 5.0]]
    
    # Verificar que al llamar nuevamente se use la caché
    embeddings_cached = openai_embedder.embed(texts, model="text-embedding-ada-002", cache_ttl=3600)
    assert embeddings_cached == embeddings

def test_embed_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    texts = ["Prueba"]
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY no está configurada"):
        openai_embedder.embed(texts)

def test_embed_api_error(monkeypatch):
    # Configurar la variable de entorno para la API key
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    # Forzar que la función dummy lance una excepción
    def dummy_fail(*args, **kwargs):
        raise Exception("Fallo simulado")
    monkeypatch.setattr(openai_embedder, "openai", type("dummy", (), {"Embedding": type("DummyEmbedding", (), {"create": dummy_fail})}))
    
    texts = ["Error"]
    with pytest.raises(RuntimeError, match="Error generando embeddings:"):
        openai_embedder.embed(texts)
