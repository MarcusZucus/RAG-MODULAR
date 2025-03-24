"""
metrics.py – Módulo Estado-del-Arte para Métricas y Medición de Rendimiento en el Sistema RAG.

Características principales:
  - Decorador measure_performance para medir tiempos de ejecución de funciones y registrar automáticamente la métrica.
  - API unificada para contadores, gauges y (sencillas) histogramas en memoria.
  - Manejo concurrente con locks para asegurar consistencia en entornos multihilo.
  - Integración opcional con aggregator.py o sistemas externos (Prometheus, StatsD).
  - Listo para producción: robusto, escalable y extensible.

Integración con aggregator:
  - Se puede usar aggregator.record_metric() tras cada inserción local si se desea un backend unificado.
  - O exportar manualmente con get_all_metrics() para su posterior ingesta.

Uso:
  - Llamar a init_metrics_system() si se requiere configuración inicial.
  - Usar register_counter("my_counter") y luego inc("my_counter") para contadores.
  - Usar record_time(...) para medir tiempos en lugar de un decorador, si se prefiere.
  - Decorador @measure_performance para funciones.

Histograma minimalista:
  - register_histogram("response_time", buckets=[0.1, 0.5, 1.0, 2.0])
  - add_histogram_value("response_time", 0.3)
    => Internamente se incrementan contadores en los buckets correctos.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
import functools
import logging

logger = logging.getLogger("MetricsLogger")
logger.setLevel(logging.DEBUG)

_LOCK = threading.Lock()

# Estructuras internas
_COUNTERS = {}
_GAUGES = {}
_HISTOGRAMS = {}

# Decorador para medir el rendimiento de funciones
def measure_performance(metric_name: str):
    """
    Decorador que mide el tiempo de ejecución de la función decorada y
    registra la métrica en un histogram o en aggregator.
    
    Args:
        metric_name (str): Nombre de la métrica (p. ej. "function_latency").

    Ejemplo:
        @measure_performance("db_query_time")
        def my_db_query():
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                logger.debug(f"Métrica '{metric_name}' => {elapsed:.6f} seg")
                # Se podría usar una histogram (si está registrada) o un counter
                with _LOCK:
                    if metric_name in _HISTOGRAMS:
                        add_histogram_value(metric_name, elapsed)
                    else:
                        # Si no hay histograma definido, creamos uno implícito con buckets por defecto
                        if metric_name not in _HISTOGRAMS:
                            register_histogram(metric_name, buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
                        add_histogram_value(metric_name, elapsed)
        return wrapper
    return decorator

def init_metrics_system() -> None:
    """
    Inicializa o reinicia el sistema de métricas (limpiando contadores, gauges e histogramas).
    Útil en entornos de test o si se requiere un 'reset'.
    """
    with _LOCK:
        _COUNTERS.clear()
        _GAUGES.clear()
        _HISTOGRAMS.clear()
    logger.info("Sistema de métricas inicializado/limpiado.")

# =========================
# CONTADORES
# =========================
def register_counter(name: str) -> None:
    """
    Registra un contador, si no existe ya.

    Args:
        name (str): Nombre único del contador.
    """
    with _LOCK:
        if name not in _COUNTERS:
            _COUNTERS[name] = 0
            logger.debug(f"Counter '{name}' registrado con valor inicial 0.")

def inc(name: str, amount: int = 1) -> None:
    """
    Incrementa el contador en 'amount'.

    Args:
        name (str): Nombre del contador a incrementar.
        amount (int): Valor a incrementar (default=1).
    """
    with _LOCK:
        if name not in _COUNTERS:
            register_counter(name)
        _COUNTERS[name] += amount
        logger.debug(f"Counter '{name}' incrementado en {amount}, total={_COUNTERS[name]}.")

# =========================
# GAUGES
# =========================
def register_gauge(name: str, initial: float = 0.0) -> None:
    """
    Registra un gauge con valor inicial.

    Args:
        name (str): Nombre del gauge.
        initial (float): Valor inicial.
    """
    with _LOCK:
        if name not in _GAUGES:
            _GAUGES[name] = initial
            logger.debug(f"Gauge '{name}' registrado con valor inicial {initial}.")

def set_gauge(name: str, value: float) -> None:
    """
    Ajusta el valor del gauge a 'value'.

    Args:
        name (str): Nombre del gauge.
        value (float): Nuevo valor.
    """
    with _LOCK:
        if name not in _GAUGES:
            register_gauge(name, initial=value)
        else:
            _GAUGES[name] = value
        logger.debug(f"Gauge '{name}' seteado a {value}.")

def inc_gauge(name: str, amount: float = 1.0) -> None:
    """
    Incrementa el gauge en 'amount'.

    Args:
        name (str): Nombre del gauge.
        amount (float): Valor a sumar.
    """
    with _LOCK:
        if name not in _GAUGES:
            register_gauge(name, initial=amount)
        else:
            _GAUGES[name] += amount
        logger.debug(f"Gauge '{name}' incrementado en {amount}, total={_GAUGES[name]}.")

# =========================
# HISTOGRAMAS
# =========================
def register_histogram(name: str, buckets: List[float]) -> None:
    """
    Registra un histograma con ciertos buckets. Se guarda internamente como:
    {
      "buckets": [0.1, 0.5, 1.0, 2.0],
      "counts": [0, 0, 0, 0, 0],  # uno más que la longitud, para "mayor a último"
      "sum": 0.0,
      "total_count": 0
    }

    Args:
        name (str): Nombre del histograma.
        buckets (List[float]): Límites de buckets (orden ascendente).
    """
    with _LOCK:
        if name in _HISTOGRAMS:
            logger.warning(f"Histograma '{name}' ya existe, no se sobrescribe.")
            return
        # Asegurar orden de buckets
        sorted_buckets = sorted(buckets)
        _HISTOGRAMS[name] = {
            "buckets": sorted_buckets,
            "counts": [0]*(len(sorted_buckets)+1),
            "sum": 0.0,
            "total_count": 0
        }
        logger.debug(f"Histograma '{name}' registrado con buckets={sorted_buckets}.")

def add_histogram_value(name: str, value: float) -> None:
    """
    Añade un valor a un histograma existente, incrementando el bucket correspondiente.

    Args:
        name (str): Nombre del histograma.
        value (float): Valor a clasificar.
    """
    with _LOCK:
        hist = _HISTOGRAMS.get(name)
        if not hist:
            logger.error(f"add_histogram_value() llamado para '{name}' que no está registrado.")
            return
        # Actualizar sum y total_count
        hist["sum"] += value
        hist["total_count"] += 1
        # Encontrar bucket
        inserted = False
        for i, b in enumerate(hist["buckets"]):
            if value <= b:
                hist["counts"][i] += 1
                inserted = True
                break
        if not inserted:
            # Se incrementa el último (excede último bucket)
            hist["counts"][-1] += 1
        logger.debug(f"Histograma '{name}' + value={value}, sum={hist['sum']}, count={hist['total_count']}.")

# =========================
# EXPORT / GET
# =========================
def get_all_metrics() -> Dict[str, Any]:
    """
    Retorna una estructura con todos los contadores, gauges e histogramas.
    """
    with _LOCK:
        # Clonar estructuras
        data = {
            "counters": dict(_COUNTERS),
            "gauges": dict(_GAUGES),
            "histograms": {}
        }
        for hname, hist in _HISTOGRAMS.items():
            data["histograms"][hname] = {
                "buckets": hist["buckets"],
                "counts": list(hist["counts"]),
                "sum": hist["sum"],
                "total_count": hist["total_count"]
            }
        return data

def record_time(metric_name: str, elapsed: float) -> None:
    """
    Añade una métrica de tiempo (segundos) a un histograma, creando el histograma si no existe.
    Similar al decorador measure_performance, pero manual.

    Args:
        metric_name (str): Nombre de la métrica histograma.
        elapsed (float): Tiempo transcurrido (segundos).
    """
    with _LOCK:
        if metric_name not in _HISTOGRAMS:
            # Registrar un histograma por defecto
            register_histogram(metric_name, buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
        add_histogram_value(metric_name, elapsed)
        logger.debug(f"Tiempo {elapsed} seg registrado en histograma '{metric_name}'.")
