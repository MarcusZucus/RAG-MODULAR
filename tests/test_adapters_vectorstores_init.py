"""
test_adapters_vectorstores_init.py – Pruebas Extremas para el __init__.py de VectorStores

Objetivos:
  1. Validar el descubrimiento dinámico de módulos .py en adapters/VectorStores.
  2. Probar la recarga forzada (force_reload) y la consistencia de VECTORSTORE_REGISTRY.
  3. Asegurar que no haya recargas innecesarias si ya están cargados.
  4. Manejo de concurrencia: múltiples hilos llamando load_vectorstores_adapters().
  5. Comprobar la existencia de métodos relevantes (por ej. add(), search(), reindex()) en los módulos.

Este test asume que existen archivos como faiss_store.py, chroma_store.py, etc., en la carpeta real.
"""

import pytest
import threading
from adapters.VectorStores import __init__ as vs_init

def test_load_vectorstores_adapters_once():
    """
    Verifica que se carguen correctamente los adaptadores y no se duplique la carga si no se fuerza reload.
    """
    vs_init.load_vectorstores_adapters(force_reload=True)
    initial_registry = dict(vs_init.VECTORSTORE_REGISTRY)

    # Sin force_reload => no debe cambiar
    vs_init.load_vectorstores_adapters(force_reload=False)
    second_registry = dict(vs_init.VECTORSTORE_REGISTRY)

    assert initial_registry == second_registry
    assert len(initial_registry) > 0  # Se espera al menos un .py (faiss_store, chroma_store, etc.)

def test_get_available_vectorstores():
    """
    Fuerza que _LOADED = False para ver si get_available_vectorstores() lo carga automáticamente.
    """
    vs_init._LOADED = False
    registry = vs_init.get_available_vectorstores()
    assert len(registry) > 0
    assert vs_init._LOADED is True

def test_force_reload():
    """
    Elimina manualmente un adaptador, luego fuerza reload y comprueba que se restaure.
    """
    vs_init.load_vectorstores_adapters(force_reload=True)
    count_before = len(vs_init.VECTORSTORE_REGISTRY)

    if count_before > 1:
        removed_key = next(iter(vs_init.VECTORSTORE_REGISTRY))
        del vs_init.VECTORSTORE_REGISTRY[removed_key]
        count_mid = len(vs_init.VECTORSTORE_REGISTRY)
        assert count_mid == (count_before - 1)

        # Al forzar de nuevo la recarga, debe volver al recuento original
        vs_init.load_vectorstores_adapters(force_reload=True)
        count_after = len(vs_init.VECTORSTORE_REGISTRY)
        assert count_after == count_before

def test_mock_methods_in_adapters():
    """
    Comprueba la existencia de métodos típicos (add, search, remove, reindex) en al menos un adaptador.
    """
    vs_init.load_vectorstores_adapters(force_reload=True)
    found_one = False

    for name, mod in vs_init.VECTORSTORE_REGISTRY.items():
        if hasattr(mod, "add") and hasattr(mod, "search"):
            # Ejemplo: ver si la función add() es llamable
            found_one = True
        # Podríamos chequear reindex() o remove(), etc. si se desea.
    assert found_one, "Se esperaba al menos un adaptador con métodos add() y search()"

def test_concurrent_load():
    """
    Múltiples hilos llamando load_vectorstores_adapters() => no debe crear problemas de carrera.
    """
    def worker():
        vs_init.load_vectorstores_adapters(force_reload=False)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert vs_init._LOADED is True
    assert len(vs_init.VECTORSTORE_REGISTRY) > 0
