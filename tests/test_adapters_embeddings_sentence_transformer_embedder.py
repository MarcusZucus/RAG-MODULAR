"""
test_adapters_embeddings_sentence_transformer_embedder.py – Pruebas avanzadas para el adaptador
sentence_transformer_embedder.py, cubriendo:

  1. Creación y carga inicial del modelo.
  2. Cacheo de resultados.
  3. Chunking de textos largos y promedio de embeddings.
  4. Concurrencia en la carga del modelo.
  5. Manejo de errores y service_detector no disponible.
"""

import pytest
import os
import time
import threading
from unittest.mock import patch, MagicMock

from adapters.Embeddings import sentence_transformer_embedder
from utils.cache_manager import _cache  # para limpiar la cache entre tests

@pytest.fixture
def clear_cache():
    # Limpia la caché antes y después de cada test
    _cache.clear()
    yield
    _cache.clear()

@pytest.fixture
def mock_availability(monkeypatch):
    """
    Fuerza check_service_availability("sentence_transformer") a True por defecto.
    """
    def dummy_check(service_name):
        if service_name == "sentence_transformer":
            return True
        return False
    monkeypatch.setattr("adapters.Embeddings.sentence_transformer_embedder.check_service_availability", dummy_check)

@pytest.fixture
def mock_model(monkeypatch):
    """
    Simula la carga de un modelo SentenceTransformer y la generación de embeddings en minúsculas.
    """
    fake_model = MagicMock()
    def fake_encode(texts, batch_size=16):
        # Retorna embeddings dummy basados en la longitud de cada texto
        # p. ej. [1.0, 1.0, ..., 1.0] (dim=3) repetido la longitud del texto
        results = []
        for t in texts:
            dim = 3
            val = float(len(t))
            results.append([val]*dim)
        return results

    fake_model.encode.side_effect = fake_encode

    # Para simular la función SentenceTransformer(...) que retorna fake_model
    mock_transformer = MagicMock(return_value=fake_model)
    monkeypatch.setattr("adapters.Embeddings.sentence_transformer_embedder.SentenceTransformer", mock_transformer)

def test_create_sentence_transformer_embedder():
    result = sentence_transformer_embedder.create()
    assert result == "sentence_transformer_embedder_creado"

def test_embed_simple(mock_availability, mock_model, clear_cache):
    texts = ["Hola", "Mundo"]
    emb = sentence_transformer_embedder.embed(texts, enable_chunking=False)
    assert len(emb) == 2
    # Cada embedding es de dimensión 3, con un valor = len(text)
    assert emb[0] == [4.0, 4.0, 4.0]
    assert emb[1] == [5.0, 5.0, 5.0]

def test_embed_with_chunking(mock_availability, mock_model, clear_cache):
    # Texto muy largo (más de chunk_size)
    text = "A" * 10  # largo=10
    # set chunk_size=4 => se divide en [4,4,2]
    emb = sentence_transformer_embedder.embed(
        [text],
        enable_chunking=True,
        chunk_size=4
    )
    assert len(emb) == 1
    # El chunking genera 3 embeddings: [4.0,4.0,4.0], [4.0,4.0,4.0], [2.0,2.0,2.0]
    # Se promedian => ( (4+4+2)/3, ... ) => (10/3, 10/3, 10/3 ) => 3.333...
    # Dependiendo de la semántica del average, se hace sum(sub_emb) / len(sub_emb)
    # Revisamos un valor aproximado
    assert abs(emb[0][0] - 3.3333333) < 0.001

def test_cache_mechanism(mock_availability, mock_model, clear_cache):
    texts = ["Hola", "Mundo"]
    # Primera vez -> no hay caché
    emb1 = sentence_transformer_embedder.embed(texts)
    # Segunda vez -> caché
    emb2 = sentence_transformer_embedder.embed(texts)
    assert emb1 == emb2

def test_concurrent_load(mock_availability, mock_model, clear_cache):
    """
    Verifica que no haya race conditions cuando varios hilos llaman a embed() simultáneamente.
    Se simulan 5 hilos de embed con los mismos textos.
    """
    texts = ["Concurrente", "Prueba", "MultiThread"]

    results = []
    def worker():
        res = sentence_transformer_embedder.embed(texts)
        results.append(res)

    threads = []
    for _ in range(5):
        th = threading.Thread(target=worker)
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    # Todos deberían recibir el mismo resultado
    for r in results[1:]:
        assert r == results[0]

def test_service_unavailable(monkeypatch):
    """
    Simula que check_service_availability('sentence_transformer') devuelva False, se espera RuntimeError.
    """
    def dummy_check(_):
        return False
    monkeypatch.setattr("adapters.Embeddings.sentence_transformer_embedder.check_service_availability", dummy_check)
    with pytest.raises(RuntimeError, match="no disponible"):
        sentence_transformer_embedder.embed(["Test"])
