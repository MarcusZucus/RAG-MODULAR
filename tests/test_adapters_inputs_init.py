"""
test_adapters_inputs_init.py – Pruebas Extremas para el __init__.py de Inputs

Verifica:
  1. Descubrimiento dinámico de módulos .py en adapters/Inputs.
  2. Registro global en INPUTS_REGISTRY.
  3. force_reload para recargar y vaciar el registro previo.
  4. Llamado concurrente, asegurando consistencia.
  5. Chequeo opcional de funciones como load() o create() en los módulos detectados.
"""

import os
import pytest
import threading
from adapters.Inputs import __init__ as inputs_init

def test_load_inputs_adapters_once(monkeypatch):
    # Forzar recarga primero
    inputs_init.load_inputs_adapters(force_reload=True)
    registry_initial = dict(inputs_init.INPUTS_REGISTRY)

    # Llamar de nuevo sin force => no debería cambiar
    inputs_init.load_inputs_adapters(force_reload=False)
    registry_second = dict(inputs_init.INPUTS_REGISTRY)

    assert registry_initial == registry_second
    assert len(registry_initial) > 0  # Se asume que hay algún loader (json_loader, etc.)

def test_get_available_inputs():
    # Forzamos estado de _LOADED a False para ver si get_available_inputs() los carga
    inputs_init._LOADED = False
    registry = inputs_init.get_available_inputs()
    assert len(registry) > 0
    assert inputs_init._LOADED is True

def test_force_reload():
    inputs_init.load_inputs_adapters(force_reload=True)
    length_before = len(inputs_init.INPUTS_REGISTRY)

    if length_before > 1:
        # Eliminamos uno de los keys manualmente
        removed_key = next(iter(inputs_init.INPUTS_REGISTRY))
        del inputs_init.INPUTS_REGISTRY[removed_key]

        length_mid = len(inputs_init.INPUTS_REGISTRY)
        assert length_mid == length_before - 1

        # force_reload() debería restaurar la lista original
        inputs_init.load_inputs_adapters(force_reload=True)
        length_after = len(inputs_init.INPUTS_REGISTRY)
        assert length_after == length_before

def test_mock_module_methods():
    inputs_init.load_inputs_adapters(force_reload=True)
    found_loader = False

    for name, mod in inputs_init.INPUTS_REGISTRY.items():
        if hasattr(mod, "load"):
            # No llamamos load() real para no disparar I/O, pero verificamos su presencia
            found_loader = True
        if hasattr(mod, "create"):
            # Igual, podemos hacer un create() si se desea testear
            resp = mod.create()
            assert isinstance(resp, str)
            found_loader = True

    assert found_loader, "Se esperaba al menos un módulo con método load() o create()"

def test_concurrent_load():
    """
    Varias hilos llamando load_inputs_adapters() sin force => no da colisiones.
    """
    def worker():
        inputs_init.load_inputs_adapters(force_reload=False)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert inputs_init._LOADED is True
    assert len(inputs_init.INPUTS_REGISTRY) > 0
