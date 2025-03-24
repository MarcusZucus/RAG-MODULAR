import os
import time
import pytest
import openai  # Importar openai para poder referenciar openai.error
from unittest.mock import MagicMock

# Importamos el módulo a testear
from adapters.LLMs import openai_generator

# Clase Dummy para simular respuesta de OpenAI.ChatCompletion.create
class DummyChatCompletionResponse:
    def __init__(self, content):
        self.choices = [self.DummyChoice(content)]
    
    class DummyChoice:
        def __init__(self, content):
            self.message = {"content": content}

    def __getitem__(self, key):
        if key == "choices":
            return self.choices
        raise KeyError(key)

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Asegurarse de limpiar la variable OPENAI_API_KEY antes y después de cada prueba.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    yield
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

def test_generate_without_api_key(monkeypatch):
    # Sin definir OPENAI_API_KEY, debe lanzarse RuntimeError.
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY no está configurada"):
        openai_generator.generate("Test prompt")

def test_generate_success(monkeypatch):
    # Configurar la API key para la prueba.
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")

    # Simular la función openai.ChatCompletion.create en el módulo openai_generator
    dummy_response = DummyChatCompletionResponse("Respuesta de prueba")
    dummy_create = MagicMock(return_value=dummy_response)
    monkeypatch.setattr(openai_generator.openai.ChatCompletion, "create", dummy_create)

    prompt = "Hola, ¿cómo estás?"
    response = openai_generator.generate(prompt, max_tokens=50)
    assert response == "Respuesta de prueba"
    dummy_create.assert_called_once()

def test_generate_retry(monkeypatch):
    # Configurar la API key.
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")

    # Simular errores transitorios en los primeros dos intentos y éxito en el tercero.
    call_count = {"count": 0}

    def dummy_create(**kwargs):
        if call_count["count"] < 2:
            call_count["count"] += 1
            raise openai.error.RateLimitError("Rate limit exceeded")
        return DummyChatCompletionResponse("Respuesta después de reintentos")

    monkeypatch.setattr(openai_generator.openai.ChatCompletion, "create", dummy_create)
    
    start_time = time.time()
    response = openai_generator.generate("Test retry prompt", retries=3, backoff_factor=1.5)
    end_time = time.time()
    # Verificar que se intentaron al menos dos reintentos
    assert call_count["count"] == 2
    assert response == "Respuesta después de reintentos"
    # Comprobar que se aplicó cierto retardo (mínimo)
    assert (end_time - start_time) >= (1 + 1.5)

def test_generate_api_error(monkeypatch):
    # Configurar la API key.
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")

    # Simular un error crítico (por ejemplo, APIError) que no se reintente.
    def dummy_create(**kwargs):
        raise openai.error.APIError("Critical API error")

    monkeypatch.setattr(openai_generator.openai.ChatCompletion, "create", dummy_create)
    
    with pytest.raises(RuntimeError, match="Error en la API de OpenAI: Critical API error"):
        openai_generator.generate("Prompt de error")
