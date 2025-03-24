"""
test_core_interfaces_input_source.py – Pruebas avanzadas para la interfaz InputSource.

Valida:
  1. Creación e instanciación de un DummyInputSource que hereda de InputSource.
  2. Ciclo de vida completo: initialize -> validate -> load_data -> shutdown.
  3. Bloqueo de secuencias incorrectas (llamar load_data antes de validate, etc.).
  4. Manejo de resultados y uso de post_load_data.
"""

import pytest
from core.interfaces.input_source import InputSource
from core.interfaces.base import ComponentState

# --------------------------------------------------
# Dummy de ejemplo
# --------------------------------------------------

class DummyInputSource(InputSource):
    """
    Implementación ficticia para probar la interfaz InputSource.
    """

    def __init__(self):
        super().__init__()
        self._initialized_resources = False
        self._validated_ok = False
        self._loaded_docs = []

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def metadata(self):
        return {
            "name": "DummyInputSource",
            "description": "Un cargador de datos ficticio para pruebas.",
            "dependencies": ["test_only"],
            "compatibility": ">=0.1.0"
        }

    def _do_initialize(self) -> None:
        # Simulamos la apertura de un recurso, por ejemplo, un archivo/endpoint
        self._initialized_resources = True

    def _do_validate(self) -> None:
        # Chequeamos que la supuesta conexión esté OK
        if not self._initialized_resources:
            raise RuntimeError("No se inicializó correctamente antes de validar.")
        self._validated_ok = True

    def _do_shutdown(self) -> None:
        # Liberamos el recurso
        self._initialized_resources = False

    def load_data(self, *args, **kwargs):
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar load_data() en estado {self.state.name}. Debe estar VALIDATED.")

        # Simulamos la obtención de documentos
        docs = [
            {"id": "doc1", "texto": "Dummy data", "metadata": {"source": "dummy"}},
            {"id": "doc2", "texto": "Another doc", "metadata": {"source": "dummy"}}
        ]
        self._loaded_docs = docs
        self.post_load_data(docs)
        return docs

# --------------------------------------------------
# Test principal
# --------------------------------------------------

def test_input_source_lifecycle():
    comp = DummyInputSource()

    # 1. Estado CREATED
    assert comp.state == ComponentState.CREATED

    # 2. initialize
    comp.initialize()
    assert comp.state == ComponentState.INITIALIZED
    assert comp._initialized_resources is True

    # 3. validate
    comp.validate()
    assert comp.state == ComponentState.VALIDATED
    assert comp._validated_ok is True

    # 4. load_data
    docs = comp.load_data()
    assert len(docs) == 2
    assert comp._loaded_docs == docs

    # 5. shutdown
    comp.shutdown()
    assert comp.state == ComponentState.SHUTDOWN
    assert comp._initialized_resources is False

def test_load_data_without_validate():
    """
    Verifica que intentar load_data() antes de validate() lanza excepción.
    """
    comp = DummyInputSource()
    comp.initialize()
    # No llamamos a comp.validate()
    with pytest.raises(RuntimeError, match="Debe estar VALIDATED"):
        comp.load_data()

def test_shutdown_early():
    """
    Si se hace shutdown tras initialize() (antes de validate()), se permite en la implementación base
    (pues en 'base.py' se permite el shutdown si state es INITIALIZED o VALIDATED).
    """
    comp = DummyInputSource()
    comp.initialize()
    comp.shutdown()
    assert comp.state == ComponentState.SHUTDOWN

def test_metadata_and_version():
    comp = DummyInputSource()
    assert comp.version == "0.1.0"
    md = comp.metadata
    assert md["name"] == "DummyInputSource"
    assert md["compatibility"] == ">=0.1.0"
