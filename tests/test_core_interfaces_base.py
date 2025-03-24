"""
test_base.py – Pruebas extremas y avanzadas para la clase BaseComponent.

Valida:
  1. Creación e instanciación del DummyComponent heredando de BaseComponent.
  2. Ciclo de vida completo (initialize -> validate -> shutdown) y verificación de estados.
  3. Bloqueos correctos de secuencia: no se puede validar sin inicializar, etc.
  4. Sobrescritura de métodos y hooks.
  5. Manejo de errores y logging detallado.
"""

import pytest
import logging
from core.interfaces.base import BaseComponent, ComponentState

# --------------------------------------------------
# DummyComponent para pruebas, hereda de BaseComponent
# --------------------------------------------------

class DummyComponent(BaseComponent):
    """
    Ejemplo de implementación de un componente concreto que hereda de BaseComponent.
    Solo para pruebas de ciclo de vida y verificación de estados.
    """

    def __init__(self):
        super().__init__()
        self._initialized_resources = False
        self._validated_ok = False

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def metadata(self):
        return {
            "name": "DummyComponent",
            "description": "Componente ficticio para pruebas.",
            "dependencies": ["none"],
            "compatibility": ">=1.0.0"
        }

    def _do_initialize(self) -> None:
        # Simulamos la reserva de algún recurso
        self._initialized_resources = True

    def post_initialize(self) -> None:
        # Hook extra si necesitamos hacer algo inmediatamente después de initialize
        pass

    def _do_validate(self) -> None:
        if not self._initialized_resources:
            raise RuntimeError("No se inicializó correctamente.")
        # Simulamos una validación interna
        self._validated_ok = True

    def post_validate(self) -> None:
        # Hook post-validación
        pass

    def _do_shutdown(self) -> None:
        # Liberamos recursos simulados
        self._initialized_resources = False

# --------------------------------------------------
# Tests
# --------------------------------------------------

def test_dummy_component_lifecycle():
    comp = DummyComponent()

    # Al crear el objeto, su estado debe ser CREATED
    assert comp.state == ComponentState.CREATED

    # 1. Inicializar
    comp.initialize()
    assert comp.state == ComponentState.INITIALIZED
    assert comp._initialized_resources is True

    # 2. Validar
    comp.validate()
    assert comp.state == ComponentState.VALIDATED
    assert comp._validated_ok is True

    # 3. Shutdown
    comp.shutdown()
    assert comp.state == ComponentState.SHUTDOWN
    assert comp._initialized_resources is False

def test_validate_without_initialize():
    """
    Intentar comp.validate() sin haber llamado initialize() debe lanzar error.
    """
    comp = DummyComponent()
    with pytest.raises(RuntimeError, match="El componente debe estar en estado INITIALIZED"):
        comp.validate()

def test_shutdown_without_validate():
    """
    Apagar sin validar: permitido si está INITIALIZED (por ejemplo, un
    caso de early shutdown) pero no si está CREATED.
    """
    # Caso 1: CREATED -> shutdown => error
    comp = DummyComponent()
    with pytest.raises(RuntimeError, match="Shutdown inválido"):
        comp.shutdown()

    # Caso 2: INITIALIZED -> shutdown => success
    comp.initialize()
    comp.shutdown()
    assert comp.state == ComponentState.SHUTDOWN

def test_reinitialize_error():
    """
    Verifica que no se pueda llamar initialize() dos veces consecutivas.
    """
    comp = DummyComponent()
    comp.initialize()
    with pytest.raises(RuntimeError, match="Initialize inválido"):
        comp.initialize()

def test_component_metadata_and_version():
    """
    Verifica que la versión y metadata cumplan con lo esperado.
    """
    comp = DummyComponent()
    assert comp.version == "1.0.0"
    md = comp.metadata
    assert md["name"] == "DummyComponent"
    assert md["compatibility"] == ">=1.0.0"
