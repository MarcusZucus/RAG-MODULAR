import os
import pytest
from adapters.LLMs import local_llm_generator

# Definimos un pipeline dummy para simular el comportamiento de un modelo local
class DummyPipeline:
    def __call__(self, prompt, max_length, do_sample):
        # Retorna una respuesta dummy basada en el prompt
        return [{"generated_text": f"Respuesta dummy para: {prompt}"}]

# Función dummy para simular la carga exitosa del modelo local
def dummy_load_local_model():
    return DummyPipeline()

def test_generate_success(monkeypatch):
    """
    Verifica que, usando un pipeline dummy, la función generate retorne la respuesta esperada.
    """
    monkeypatch.setattr(local_llm_generator, "load_local_model", dummy_load_local_model)
    prompt = "Hola, ¿cómo estás?"
    response = local_llm_generator.generate(prompt)
    assert "Respuesta dummy para:" in response

def test_load_local_model_without_env(monkeypatch):
    """
    Verifica que se lance un RuntimeError cuando no está definida la variable LOCAL_LLM_MODEL_PATH.
    """
    monkeypatch.delenv("LOCAL_LLM_MODEL_PATH", raising=False)
    with pytest.raises(RuntimeError, match="LOCAL_LLM_MODEL_PATH no está configurado"):
        local_llm_generator.load_local_model()

def test_load_local_model_with_invalid_path(monkeypatch):
    """
    Simula que la carga del modelo falla debido a una ruta inválida.
    """
    monkeypatch.setenv("LOCAL_LLM_MODEL_PATH", "ruta_invalida")
    # Forzamos que la función pipeline lance una excepción al cargar
    def dummy_pipeline(*args, **kwargs):
        raise Exception("Carga fallida")
    monkeypatch.setattr("adapters.LLMs.local_llm_generator.pipeline", dummy_pipeline)
    with pytest.raises(RuntimeError, match="Error cargando el modelo local"):
        local_llm_generator.load_local_model()
    monkeypatch.delenv("LOCAL_LLM_MODEL_PATH", raising=False)
