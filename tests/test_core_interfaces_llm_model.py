"""
test_core_interfaces_llm_model.py – Pruebas Avanzadas para la Interfaz LLMModel.

Valida:
  1. Creación e instanciación de una subclase dummy de LLMModel.
  2. Ciclo de vida completo: initialize -> validate -> generate -> shutdown.
  3. Bloqueo de secuencias incorrectas (llamar generate() antes de validate).
  4. Opcionalidad de generate_stream() y post_generate().
  5. Múltiples pruebas de error, reintentos (dummy), etc.
"""

import pytest
from typing import Generator, Optional
from core.interfaces.llm_model import LLMModel, ComponentState
import logging

logger = logging.getLogger("TestLLMLogger")


# --------------------------------------------------
# Dummy LLM Model
# --------------------------------------------------
class DummyLLM(LLMModel):
    """
    Implementación ficticia para pruebas de la interfaz LLMModel.
    Soporta:
      - Ejecución normal de generate().
      - Opcional: streaming tokens.
      - post_generate() para limpiar la respuesta.
    """

    def __init__(self, fail_times=0):
        """
        fail_times: cuántas veces generate() falla antes de tener éxito (simula reintentos).
        """
        super().__init__()
        self._fail_times = fail_times
        self._internal_resources_ready = False

    def _do_initialize(self) -> None:
        # Simula la carga de un modelo interno
        logger.debug("[DummyLLM] _do_initialize() -> cargando modelo local ficticio.")
        self._internal_resources_ready = True

    def _do_validate(self) -> None:
        # Verifica si la “carga” está lista
        if not self._internal_resources_ready:
            raise RuntimeError("Modelo no inicializado.")
        logger.debug("[DummyLLM] _do_validate() -> todo OK.")

    def _do_shutdown(self) -> None:
        # Liberamos recursos
        self._internal_resources_ready = False
        logger.debug("[DummyLLM] _do_shutdown() -> recursos liberados.")

    def generate(self, prompt: str, **kwargs) -> str:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar generate() en estado {self.state.name}. Debe estar VALIDATED.")
        if not prompt:
            raise ValueError("Prompt vacío.")
        if self._fail_times > 0:
            self._fail_times -= 1
            raise RuntimeError("Fallo simulado en generate()")

        # Retorna una respuesta dummy
        response = f"Respuesta-Dummy para: {prompt}"
        # post-generate
        return self.post_generate(response)

    def generate_stream(self, prompt: str, **kwargs) -> Optional[Generator[str, None, None]]:
        if self.state != ComponentState.VALIDATED:
            raise RuntimeError(f"No se puede invocar generate_stream() en estado {self.state.name}.")
        if not prompt:
            raise ValueError("Prompt vacío en streaming.")
        # Simulamos un streaming de tokens
        tokens = ["Dummy", "streamed", "tokens", "for", prompt]
        def token_generator():
            for tk in tokens:
                yield tk
        return token_generator()

    def post_generate(self, response: str) -> str:
        # Ejemplo: quitamos subcadena "Dummy"
        return response.replace("Dummy", "XXX")


# --------------------------------------------------
# Tests
# --------------------------------------------------
def test_llm_lifecycle():
    llm = DummyLLM()

    assert llm.state == ComponentState.CREATED
    # initialize
    llm.initialize()
    assert llm.state == ComponentState.INITIALIZED
    # validate
    llm.validate()
    assert llm.state == ComponentState.VALIDATED

    # generate
    prompt = "Hola mundo"
    resp = llm.generate(prompt)
    assert "XXX" in resp  # Porque post_generate() reemplaza "Dummy" con "XXX"
    assert "Hola mundo" in resp

    # shutdown
    llm.shutdown()
    assert llm.state == ComponentState.SHUTDOWN

def test_generate_before_validate():
    llm = DummyLLM()
    llm.initialize()
    # No llamamos validate()
    with pytest.raises(RuntimeError, match="Debe estar VALIDATED"):
        llm.generate("Hola")

def test_streaming_tokens():
    llm = DummyLLM()
    llm.initialize()
    llm.validate()

    gen = llm.generate_stream("stream_test")
    tokens = list(gen)
    assert tokens == ["Dummy", "streamed", "tokens", "for", "stream_test"]

def test_streaming_before_validate():
    llm = DummyLLM()
    llm.initialize()
    with pytest.raises(RuntimeError, match="Debe estar VALIDATED"):
        _ = llm.generate_stream("prueba")

def test_fail_times():
    """
    Prueba que simulate n fallos antes de tener éxito.
    """
    llm = DummyLLM(fail_times=2)
    llm.initialize()
    llm.validate()

    with pytest.raises(RuntimeError, match="Fallo simulado"):
        llm.generate("Test1")
    with pytest.raises(RuntimeError, match="Fallo simulado"):
        llm.generate("Test2")
    # Tercer intento debe tener éxito
    resp = llm.generate("Test3")
    assert "Test3" in resp
    assert "Fallo simulado" not in resp

def test_empty_prompt():
    llm = DummyLLM()
    llm.initialize()
    llm.validate()
    with pytest.raises(ValueError, match="Prompt vacío"):
        llm.generate("")
