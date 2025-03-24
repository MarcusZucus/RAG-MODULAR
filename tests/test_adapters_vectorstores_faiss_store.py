import pytest
import numpy as np
from adapters.VectorStores import faiss_store

# Definir un vector dummy de dimensión 4 para la prueba
DIM = 4

class DummyDocument:
    def __init__(self, doc_id, texto):
        self.id = doc_id
        self.texto = texto
    def to_dict(self):
        return {"id": self.id, "texto": self.texto, "metadata": {"origen": "test", "fecha": "2025-03-22"}}

@pytest.fixture
def faiss_instance():
    # Crear una instancia del FaissStore con dimensión DIM
    store = faiss_store.FaissStore(dim=DIM)
    return store

def test_faiss_store_initialization(faiss_instance):
    # Verificar que el índice está inicializado y el mapping está vacío
    assert faiss_instance.index.ntotal == 0
    assert faiss_instance.doc_mapping == {}

def test_add_document_success(faiss_instance):
    doc = DummyDocument("doc1", "Contenido de prueba").to_dict()
    vector = [0.1, 0.2, 0.3, 0.4]
    faiss_instance.add(doc, vector)
    # Después de agregar, ntotal debe ser 1 y mapping contener la clave 0
    assert faiss_instance.index.ntotal == 1
    assert 0 in faiss_instance.doc_mapping
    retrieved_doc = faiss_instance.doc_mapping[0]
    assert retrieved_doc["id"] == "doc1"

def test_add_document_wrong_dimension(faiss_instance):
    doc = DummyDocument("doc2", "Otro contenido").to_dict()
    vector = [0.1, 0.2]  # Incorrecto, dimensión 2 en lugar de DIM (4)
    with pytest.raises(ValueError, match="dimensión del vector"):
        faiss_instance.add(doc, vector)

def test_search_documents(faiss_instance):
    # Agregar varios documentos con vectores
    docs = [
        DummyDocument("doc1", "Texto similar 1").to_dict(),
        DummyDocument("doc2", "Texto similar 2").to_dict(),
        DummyDocument("doc3", "Texto distinto").to_dict()
    ]
    vectors = [
        [0.1, 0.2, 0.3, 0.4],
        [0.1, 0.2, 0.3, 0.45],
        [0.9, 0.8, 0.7, 0.6]
    ]
    for doc, vec in zip(docs, vectors):
        faiss_instance.add(doc, vec)
    
    # Realizar búsqueda con un vector de consulta similar a los dos primeros documentos.
    query_vector = [0.1, 0.2, 0.3, 0.42]
    results = faiss_instance.search(query_vector, k=2)
    # Se esperan 2 documentos, y los dos primeros deberían ser recuperados
    assert len(results) == 2
    ids = [d["id"] for d in results]
    assert "doc1" in ids
    assert "doc2" in ids

def test_search_wrong_dimension(faiss_instance):
    query_vector = [0.1, 0.2]  # Dimensión incorrecta
    with pytest.raises(ValueError, match="dimensión del vector de consulta"):
        faiss_instance.search(query_vector, k=1)
