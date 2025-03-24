"""
test_adapters_embeddings_init.py – Pruebas Extremas para el __init__.py de Embeddings

Valida:
  1. Carga dinámica de módulos de embeddings.
  2. Contenido de EMBEDDINGS_REGISTRY.
  3. Manejo de force_reload para recargas.
  4. Ejecución opcional de funciones create() o embed() si están definidas.
  5. Control de concurrencia.
"""

import os
import pytest
import threading
from adapters.Embeddings import __init__ as embeddings_init

def test_load_embeddings_adapters_once(monkeypatch):
    """
    Verifica que la carga se realice correctamente y solo una vez si no se fuerza reload.
    """
    # Asegurar un directorio de prueba con un dummy .py
    # Sin embargo, en la práctica, ya existen openai_embedder.py, etc.
    # Si deseas un test aislado, simularías con un directorio temporal.

    # Forzamos la recarga por si se cargaron adaptadores antes
    embeddings_init.load_embeddings_adapters(force_reload=True)
    registry_before = dict(embeddings_init.EMBEDDINGS_REGISTRY)

    # Se llama de nuevo, sin force_reload => no debe cambiar
    embeddings_init.load_embeddings_adapters(force_reload=False)
    registry_after = dict(embeddings_init.EMBEDDINGS_REGISTRY)

    assert registry_before == registry_after
    assert len(registry_before) > 0  # asumiendo que hay al menos un .py (openai_embedder, etc.)

def test_get_available_embeddings():
    """
    Verifica que get_available_embeddings() retorne el registro y que lo cargue si no lo estaba.
    """
    embeddings_init._LOADED = False  # forzamos estado
    registry = embeddings_init.get_available_embeddings()
    assert len(registry) > 0
    assert embeddings_init._LOADED is True

def test_force_reload():
    """
    Verifica que force_reload vacíe el EMBEDDINGS_REGISTRY y lo recargue.
    """
    embeddings_init.load_embeddings_adapters(force_reload=True)
    length_before = len(embeddings_init.EMBEDDINGS_REGISTRY)
    # Quitamos un módulo manualmente
    if length_before > 1:
        removed_key = next(iter(embeddings_init.EMBEDDINGS_REGISTRY))
        del embeddings_init.EMBEDDINGS_REGISTRY[removed_key]
        length_mid = len(embeddings_init.EMBEDDINGS_REGISTRY)
        assert length_mid == (length_before - 1)
        # Volvemos a forzar
        embeddings_init.load_embeddings_adapters(force_reload=True)
        length_after = len(embeddings_init.EMBEDDINGS_REGISTRY)
        # Debe regresar al conteo anterior
        assert length_after == length_before

def test_mocked_module_methods():
    """
    Opcional: si se desea probar la presencia de create() o embed() en alguno de los módulos detectados.
    """
    embeddings_init.load_embeddings_adapters(force_reload=True)
    found_one = False

    for name, mod in embeddings_init.EMBEDDINGS_REGISTRY.items():
        if hasattr(mod, "create"):
            result = mod.create()
            # Por ejemplo, "openai_embedder_creado"
            assert isinstance(result, str)
            found_one = True
        if hasattr(mod, "embed"):
            # No llamamos a .embed() real, salvo que se quiera un test con mock
            found_one = True
    
    assert found_one, "Se esperaba encontrar al menos un módulo con create() o embed()."

def test_concurrent_load():
    """
    Prueba de concurrencia: múltiples hilos llamando load_embeddings_adapters() simultáneamente.
    No debe producir errores ni recargas repetidas de forma inconsistent.
    """
    def worker():
        embeddings_init.load_embeddings_adapters(force_reload=False)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert embeddings_init._LOADED is True
    assert len(embeddings_init.EMBEDDINGS_REGISTRY) > 0
