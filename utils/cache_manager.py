import threading
import time

# Diccionario global que actuará como caché
_cache = {}
_lock = threading.Lock()

def get_cache(key: str):
    """
    Recupera el valor almacenado en la caché para una clave dada.
    Si se ha definido un TTL para la entrada y ha expirado, se elimina y se devuelve None.

    Args:
        key (str): La clave de la entrada en la caché.

    Returns:
        El valor almacenado o None si no existe o ha expirado.
    """
    with _lock:
        entry = _cache.get(key)
        if entry:
            ttl = entry.get("ttl")
            if ttl is not None:
                # Verifica si la entrada ha expirado
                if time.time() > entry["timestamp"] + ttl:
                    # Entrada expirada, la elimina de la caché
                    del _cache[key]
                    return None
            return entry["value"]
    return None

def set_cache(key: str, value, ttl: int = None):
    """
    Almacena un valor en la caché asociado a una clave.
    Se puede definir opcionalmente un TTL (tiempo de vida en segundos).

    Args:
        key (str): La clave a la que se asocia el valor.
        value: El valor a almacenar.
        ttl (int, opcional): Tiempo de vida en segundos para la entrada. Si no se define, la entrada no expira.
    """
    with _lock:
        _cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
