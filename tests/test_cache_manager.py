import time
import threading
import pytest
from utils.cache_manager import get_cache, set_cache

def test_set_and_get_cache_without_ttl():
    # Almacenar un valor sin TTL
    key = "test_key"
    value = {"data": 123}
    set_cache(key, value)
    
    # Recuperar el valor inmediatamente
    cached_value = get_cache(key)
    assert cached_value == value, "El valor almacenado no coincide con el recuperado sin TTL"

def test_set_and_get_cache_with_ttl(monkeypatch):
    key = "ttl_key"
    value = "valor_con_ttl"
    ttl = 2  # 2 segundos
    start_time = time.time()
    
    # Simular el tiempo: usamos una función lambda que incremente el tiempo
    monkeypatch.setattr(time, "time", lambda: start_time)
    
    # Almacenar el valor con TTL
    set_cache(key, value, ttl=ttl)
    
    # Inicialmente, el valor debería estar disponible
    assert get_cache(key) == value, "El valor no se recupera correctamente antes de expirar"
    
    # Simular avance del tiempo: justo antes de la expiración
    monkeypatch.setattr(time, "time", lambda: start_time + ttl - 0.1)
    assert get_cache(key) == value, "El valor se expiró prematuramente"

    # Simular avance del tiempo: después de la expiración
    monkeypatch.setattr(time, "time", lambda: start_time + ttl + 0.1)
    assert get_cache(key) is None, "El valor no fue eliminado después de expirar"

def test_cache_concurrent_access():
    """
    Prueba básica para verificar que el cache maneja acceso concurrente sin errores.
    """
    key = "concurrent_key"
    value = 42
    set_cache(key, value)
    
    results = []

    def worker():
        # Cada hilo intenta leer la misma clave
        results.append(get_cache(key))
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Todos los hilos deberían obtener el mismo valor
    assert all(result == value for result in results), "El acceso concurrente no devolvió valores consistentes"
