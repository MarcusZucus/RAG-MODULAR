"""
test_adapters_llms_init.py – Pruebas Extremas para el __init__.py de LLMs

Objetivo:
  - Verificar el proceso de descubrimiento y registro de adaptadores en LLM_REGISTRY.
  - Testear force_reload, concurrencia y presencia de métodos relevantes (p.ej. create(), generate()).
"""

import pytest
import threading
from adapters.LLMs import __init__ as llms_init

def test_llms_load_once():
    """
    Verifica que se carguen los adaptadores solo una vez si no se fuerza la recarga.
    """
    llms_init.load_llms_adapters(force_reload=True)
    initial_registry = dict(llms_init.LLM_REGISTRY)

    # Llamada sin force_reload => no debe cambiar
    llms_init.load_llms_adapters(force_reload=False)
    second_registry = dict(llms_init.LLM_REGISTRY)

    assert initial_registry == second_registry
    assert len(initial_registry) > 0  # Se asume existen archivos (openai_generator.py, local_llm_generator.py, etc.)

def test_get_available_llms():
    # Forzar que _LOADED sea False para ver si se auto-carga
    llms_init._LOADED = False
    registry = llms_init.get_available_llms()
    assert len(registry) > 0
    assert llms_init._LOADED is True

def test_force_reload():
    llms_init.load_llms_adapters(force_reload=True)
    count_before = len(llms_init.LLM_REGISTRY)

    if count_before > 1:
        # Eliminar un adaptador manualmente
        removed_key = next(iter(llms_init.LLM_REGISTRY))
        del llms_init.LLM_REGISTRY[removed_key]
        count_mid = len(llms_init.LLM_REGISTRY)
        assert count_mid == (count_before - 1)

        # Llamar force_reload => Debe restaurar
        llms_init.load_llms_adapters(force_reload=True)
        count_after = len(llms_init.LLM_REGISTRY)
        assert count_after == count_before

def test_mocked_module_functions():
    """
    Verifica la existencia de funciones create() o generate() en al menos un módulo detectado,
    sin invocarlas realmente para evitar interacciones con servicios remotos o cargas pesadas.
    """
    llms_init.load_llms_adapters(force_reload=True)
    found_llm = False

    for name, mod in llms_init.LLM_REGISTRY.items():
        if hasattr(mod, "create"):
            res = mod.create()
            assert isinstance(res, str)  # p.ej. "openai_generator_creado"
            found_llm = True
        if hasattr(mod, "generate"):
            found_llm = True

    assert found_llm, "Se esperaba encontrar al menos un LLM con método create() o generate()"

def test_concurrent_load():
    """
    Lanza varios hilos que llaman load_llms_adapters() => No debe generar inconsistencias.
    """
    def worker():
        llms_init.load_llms_adapters(force_reload=False)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert llms_init._LOADED is True
    assert len(llms_init.LLM_REGISTRY) > 0
