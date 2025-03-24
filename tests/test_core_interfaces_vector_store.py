"""
test_core_interfaces_vector_store.py – Pruebas Avanzadas para la Interfaz VectorStore.

Valida:
  1. Creación e instanciación de una subclase dummy de VectorStore.
  2. Ciclo de vida completo: initialize -> validate -> add/remove/search -> reindex -> shutdown.
  3. Bloqueo de secuencias incorrectas (llamar add() antes de validate, etc.).
  4. Manejo de resultados y verificación de dimensionamiento.
  5. Hooks u operaciones especiales (reindex, etc.).
"""

import pytest
from typing import Any, Dict, List
from core.interfaces.vector_store import VectorStore, ComponentState

# --------------------------------------------------
# Dummy de ejemplo
# --------------------------------------------------
class DummyVectorStore(VectorStore):
    """
    Implementación ficticia para probar la interfaz VectorStore.
    Almacena documentos en memoria en un dict y simula un índice vectorial.
    """

    def __init__(self, embedding_dim=4):
        super().__init__()
        self._embedding_dim = embedding_dim
        self._docs = {}  # diccionario doc_id -> doc
        self._index_built = False

    def add(self, document: Dict[str, Any], vector: List[float]) -> None:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar add() en estado {self.state.name}. Debe estar VALIDATED.")
        if len(vector) != self._embedding_dim:
            raise ValueError("La dimensión del vector es incorrecta.")
        doc_id = document.get("id")
        if not doc_id:
            raise ValueError("Documento sin 'id'.")
        doc_copy = dict(document)
        doc_copy["vector"] = vector
        self._docs[doc_id] = doc_copy

    def remove(self, doc_id: str) -> None:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar remove() en estado {self.state.name}. Debe estar VALIDATED.")
        if doc_id not in self._docs:
            raise RuntimeError(f"Documento '{doc_id}' no existe en el índice.")
        del self._docs[doc_id]

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar search() en estado {self.state.name}. Debe estar VALIDATED.")
        if len(query_vector) != self._embedding_dim:
            raise ValueError("La dimensión del vector de consulta es incorrecta.")
        # Lógica ultra-simplificada: “ordena” por diferencia de la primera componente.
        # Solo para ejemplificar.
        docs_list = list(self._docs.values())
        docs_list.sort(key=lambda d: abs(d["vector"][0] - query_vector[0]))
        return docs_list[:k]

    def reindex(self) -> None:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede reindexar en estado {self.state.name}. Debe estar VALIDATED.")
        # Simulamos un reindex que limpia y vuelve a crear en memoria
        old_docs = self._docs.copy()
        self._docs = {}
        self._docs.update(old_docs)
        self._index_built = True

    # Implementaciones de métodos de ciclo de vida
    def _do_initialize(self) -> None:
        pass

    def _do_validate(self) -> None:
        if self._embedding_dim <= 0:
            raise RuntimeError("Dimensión de embedding inválida.")
        # Listo para la acción
        self._index_built = False

    def _do_shutdown(self) -> None:
        # Liberar memoria o lo que sea necesario
        self._docs.clear()


# --------------------------------------------------
# Test principal
# --------------------------------------------------
def test_vector_store_lifecycle():
    store = DummyVectorStore(embedding_dim=4)

    # 1. Estado CREATED
    assert store.state == ComponentState.CREATED

    # 2. initialize
    store.initialize()
    assert store.state == ComponentState.INITIALIZED

    # 3. validate
    store.validate()
    assert store.state == ComponentState.VALIDATED

    # 4. add documents
    doc1 = {"id": "doc1", "texto": "Ejemplo 1"}
    store.add(doc1, [0.1, 0.2, 0.3, 0.4])
    doc2 = {"id": "doc2", "texto": "Ejemplo 2"}
    store.add(doc2, [0.5, 0.6, 0.7, 0.8])
    assert len(store._docs) == 2

    # 5. search
    results = store.search([0.05, 0.2, 0.33, 0.4])
    assert len(results) == 2
    # doc1 debería aparecer primero por la “distancia” que definimos
    assert results[0]["id"] == "doc1"

    # 6. remove
    store.remove("doc2")
    assert len(store._docs) == 1

    # 7. reindex
    store.reindex()
    assert len(store._docs) == 1
    assert store._index_built is True

    # 8. shutdown
    store.shutdown()
    assert store.state == ComponentState.SHUTDOWN
    assert len(store._docs) == 0

def test_vector_store_wrong_dim():
    store = DummyVectorStore(embedding_dim=3)
    store.initialize()
    store.validate()

    doc = {"id": "docX", "texto": "Dimensión incorrecta"}
    with pytest.raises(ValueError, match="dimensión del vector es incorrecta"):
        store.add(doc, [0.1, 0.2, 0.3, 0.4])  # 4 en lugar de 3

def test_remove_nonexistent_document():
    store = DummyVectorStore()
    store.initialize()
    store.validate()
    with pytest.raises(RuntimeError, match="no existe en el índice"):
        store.remove("desconocido")

def test_search_with_wrong_dim():
    store = DummyVectorStore(embedding_dim=2)
    store.initialize()
    store.validate()
    doc = {"id": "doc1"}
    store.add(doc, [0.1, 0.2])
    with pytest.raises(ValueError
