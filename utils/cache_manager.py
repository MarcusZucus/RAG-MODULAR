import threading
import time
from typing import Any, Optional, Dict

# ------------------------------------------------------------------------------------
# Módulo de gestión de caché (cache_manager.py)
# ------------------------------------------------------------------------------------
# Este módulo proporciona una caché simple basada en un diccionario y bloqueos (locks)
# de threading para asegurar acceso concurrente seguro. Se incluyen funciones para:
#   1) Obtener valores de la caché (get_cache).
#   2) Guardar valores en la caché (set_cache).
#   3) Limpiar la caché completa (clear_cache).
#   4) Limpiar entradas de caché asociadas a un "schema" específico (clear_schema_cache).
#   5) Verificar si existe una clave en la caché (has_cache).
#   6) Obtener todas las claves almacenadas (get_all_keys).
#   7) Eliminar una clave específica (delete_cache_key).
#
# También soporta TTL (tiempo de vida) por entrada, de modo que se eliminen
# automáticamente los valores que hayan expirado.
# ------------------------------------------------------------------------------------

# Diccionario global que actuará como caché.
_cache: Dict[str, Dict[str, Any]] = {}

# Lock para acceso seguro a la caché en entornos multithreading.
_lock = threading.Lock()

def get_cache(key: str) -> Optional[Any]:
    """
    Recupera el valor almacenado en la caché para una clave dada.
    
    - Si se ha definido un TTL (tiempo de vida) para la entrada y ha expirado, 
      se elimina la entrada y se devuelve None.
    - De lo contrario, retorna el valor almacenado.

    Args:
        key (str): La clave de la entrada en la caché.

    Returns:
        El valor almacenado (de cualquier tipo) o None si no existe 
        o si la entrada ha expirado.
    """
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None

        ttl = entry.get("ttl")
        if ttl is not None:
            # Verifica si la entrada ha expirado (timestamp + ttl < hora actual)
            if time.time() > entry["timestamp"] + ttl:
                # Entrada expirada, se elimina de la caché
                del _cache[key]
                return None

        return entry["value"]

def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """
    Almacena un valor en la caché asociado a la clave indicada.
    Opcionalmente, se puede definir un TTL (tiempo de vida en segundos).
    Si no se define TTL, la entrada no expira automáticamente.

    Args:
        key (str): Clave que identificará el valor en la caché.
        value (Any): El valor a almacenar.
        ttl (int, opcional): Tiempo de vida en segundos para la entrada. 
                             Por defecto, None (no expira).
    """
    with _lock:
        _cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }

def has_cache(key: str) -> bool:
    """
    Verifica si existe una clave específica dentro de la caché y 
    no ha expirado su TTL (si es que se definió).

    Args:
        key (str): Clave a verificar en la caché.

    Returns:
        bool: True si la clave existe y no ha expirado, False en caso contrario.
    """
    return get_cache(key) is not None

def delete_cache_key(key: str) -> None:
    """
    Elimina de la caché la entrada asociada a la clave especificada, 
    independientemente de si ha expirado o no.

    Args:
        key (str): Clave de la entrada que se desea eliminar.
    """
    with _lock:
        if key in _cache:
            del _cache[key]

def get_all_keys() -> list:
    """
    Retorna una lista con todas las claves actuales de la caché.
    Puede ser útil para depuración o para verificar el contenido de la caché.

    Returns:
        list: Lista de claves (strings) presentes en la caché.
    """
    with _lock:
        # Antes de retornar las claves, conviene limpiar entradas expiradas
        _clean_expired_entries()
        return list(_cache.keys())

def clear_cache() -> None:
    """
    Elimina todas las entradas de la caché, independientemente de su estado o TTL.
    Útil si se necesita reiniciar la caché por completo.
    """
    with _lock:
        _cache.clear()

def clear_schema_cache(schema_prefix: str = "schema_") -> None:
    """
    Elimina de la caché todas las entradas cuyas claves contengan o comiencen 
    con un prefijo específico, típicamente relacionado con 'schema'.
    
    Por ejemplo, si en la caché hay claves como:
        - schema_user_1
        - schema_orders_2023
        - product_list
        - schema_invoices_cache
    
    y se llama clear_schema_cache("schema_"), eliminará todas las que empiecen 
    con "schema_". Si se desea un comportamiento distinto (por ejemplo, filtrar 
    'schema' en alguna parte intermedia de la clave), se puede ajustar la lógica 
    interna.

    Args:
        schema_prefix (str): Prefijo que determina las claves a eliminar.
                             Por defecto es "schema_", pero se puede personalizar.
    """
    with _lock:
        keys_to_delete = [k for k in _cache if k.startswith(schema_prefix)]
        for k in keys_to_delete:
            del _cache[k]

def _clean_expired_entries() -> None:
    """
    Función interna que elimina de la caché todas las entradas expiradas 
    según su TTL. Esto se utiliza en funciones de acceso para garantizar 
    que la caché no contenga elementos vencidos.
    """
    current_time = time.time()
    keys_expired = []
    for key, entry in _cache.items():
        ttl = entry.get("ttl")
        if ttl is not None and current_time > entry["timestamp"] + ttl:
            keys_expired.append(key)

    for key in keys_expired:
        del _cache[key]
