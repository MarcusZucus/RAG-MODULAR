"""
test_adapters_vectorstores_chroma_store.py – Pruebas avanzadas para el adaptador ChromaStore.

Cubre:
  1. Creación y configuración inicial (persistente vs en memoria).
  2. Inserción de documentos con dimensión correcta e incorrecta.
  3. Búsquedas por vector.
  4. Eliminación de documentos.
  5. Concurrencia (varios threads añadiendo o buscando).
  6. Reindexación y validación posterior.
"""

import pytest
import threading
import time
import os
from adapters.VectorStores.chroma_store import ChromaStore
from unittest.mock import patch

@pytest.fixture
def mock_chroma_availability(monkeypatch):
    """
    Fuerza check_service_availability('chroma_store') a True.
    Para simular un entorno con Chroma habilitado.
    """
    def dummy_check(service_name):
        if service_name == "chroma_store":
            return True
        return False
    monkeypatch.setattr("adapters.VectorStores.chroma_store.check_service_availability", dummy_check)

@pytest.fixture
def temp_chroma_store(tmp_path, mock_chroma_availability):
    """
    Crea una instancia de ChromaStore apuntando a un directorio temporal para persistir
    (así podemos probar la persistencia real). Se limpia al finalizar.
    """
    persist_dir = tmp_path / "chroma_data"
    persist_dir.mkdir(exist_ok=True)
    store = ChromaStore(collection_name="test_collection", embed_dim=4, persist_directory=str(persist_dir))
    yield store
    # Al finalizar, se podría limpiar si lo deseamos:
    # import shutil
    # shutil.rmtree(persist_dir, ignore_errors=True)

def test_chroma_init_inmemory(mock_chroma_availability):
    """
    Verifica que se pueda iniciar ChromaStore en modo memoria (persist_directory=None).
    """
    store = ChromaStore(collection_name="memory_collection", embed_dim=4, persist_directory=None)
    assert store.collection_name == "memory_collection"
    assert store.embed_dim == 4

def test_add_document_success(temp_chroma_store):
    doc = {"id": "doc1", "texto": "Hola mundo", "metadata": {"categoria": "test"}}
    vector = [0.1, 0.2, 0.3, 0.4]
    temp_chroma_store.add(doc, vector)
    # Buscamos para asegurar que se insertó
    results = temp_chroma_store.search([0.1, 0.2, 0.3, 0.4], k=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc1"

def test_add_document_wrong_dimension(temp_chroma_store):
    doc = {"id": "doc2", "texto": "Dimensión incorrecta", "metadata": {}}
    vector = [0.1, 0.2]  # Esperamos 4, aquí 2
    with pytest.raises(ValueError, match="dimensión del vector"):
        temp_chroma_store.add(doc, vector)

def test_remove_document(temp_chroma_store):
    # Insertamos
    temp_chroma_store.add({"id": "doc3", "texto": "Texto doc3"}, [0.9, 0.8, 0.7, 0.6])
    # Comprobamos que está
    r = temp_chroma_store.search([0.9, 0.8, 0.7, 0.6], k=1)
    assert len(r) == 1
    # Eliminamos
    temp_chroma_store.remove("doc3")
    r2 = temp_chroma_store.search([0.9, 0.8, 0.7, 0.6], k=1)
    # Ya no debería encontrarse
    assert len(r2) == 0

def test_reindex(temp_chroma_store):
    # Insertamos varios
    for i in range(3):
        doc_id = f"doc_{i}"
        v = [0.1*i, 0.2*i, 0.3*i, 0.4*i]
        temp_chroma_store.add({"id": doc_id, "texto": f"texto {i}"}, v)
    docs_before = temp_chroma_store.list_documents()
    assert len(docs_before) == 3

    # Reindexamos
    temp_chroma_store.reindex_collection()
    # Debe quedar vacío
    docs_after = temp_chroma_store.list_documents()
    assert len(docs_after) == 0

def test_concurrent_access(temp_chroma_store):
    """
    Prueba de concurrencia: varios threads añaden documentos y uno hace búsqueda simultáneamente.
    """
    def add_docs(start, end):
        for i in range(start, end):
            doc_id = f"cdoc_{i}"
            vec = [0.1*i, 0.2*i, 0.3*i, 0.4*i]
            temp_chroma_store.add({"id": doc_id, "texto": f"doc concurrente {i}"}, vec)

    threads = []
    for t in range(5):
        th = threading.Thread(target=add_docs, args=(t*10, (t+1)*10))
        th.start()
        threads.append(th)

    # Mientras tanto, hacemos una búsqueda cada 100 ms
    for _ in range(5):
        time.sleep(0.1)
        r = temp_chroma_store.search([0.2, 0.4, 0.6, 0.8], k=2)
        # Solo validamos que no explote por race conditions
        assert isinstance(r, list)

    # Esperar que terminen
    for th in threads:
        th.join()

    # Verificar que se hayan insertado 50 docs
    all_docs = temp_chroma_store.list_documents()
    assert len(all_docs) == 50
    # Buscar con un vector específico:
    sample_res = temp_chroma_store.search([0.2, 0.4, 0.6, 0.8], k=5)
    # Confirmar que no colapsa la app
    assert isinstance(sample_res, list)

def test_service_unavailable(monkeypatch):
    """
    Simula que service_detector retorna False, se debe lanzar RuntimeError.
    """
    def dummy_check(_):
        return False
    monkeypatch.setattr("adapters.VectorStores.chroma_store.check_service_availability", dummy_check)
    with pytest.raises(RuntimeError, match="no disponible"):
        _ = ChromaStore()
