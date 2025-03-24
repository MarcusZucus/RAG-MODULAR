"""
test_utils_metrics.py – Pruebas Extremas para utils/metrics.py

Cobertura:
  1. Inicialización de sistema de métricas, registro y actualización de contadores, gauges e histogramas.
  2. Uso del decorador @measure_performance.
  3. Manejo de buckets en histogramas y verificación de conteo.
  4. Concurrencia y consistencia en multihilo.
  5. Exportación de todas las métricas y validación de la estructura resultante.
"""

import pytest
import time
import threading
from utils import metrics
from math import isclose

def test_init_and_counters():
    metrics.init_metrics_system()
    data = metrics.get_all_metrics()
    assert data["counters"] == {}
    assert data["gauges"] == {}
    assert data["histograms"] == {}

    metrics.register_counter("requests_total")
    metrics.inc("requests_total")
    metrics.inc("requests_total", 2)
    result = metrics.get_all_metrics()
    assert result["counters"]["requests_total"] == 3

def test_gauges():
    metrics.init_metrics_system()
    metrics.register_gauge("memory_usage", initial=100.0)
    metrics.inc_gauge("memory_usage", 20.0)
    metrics.set_gauge("memory_usage", 150.0)
    result = metrics.get_all_metrics()
    assert isclose(result["gauges"]["memory_usage"], 150.0, rel_tol=1e-9)

def test_histogram_basic():
    metrics.init_metrics_system()
    metrics.register_histogram("response_time", buckets=[0.1, 0.5, 1.0])
    metrics.add_histogram_value("response_time", 0.05)  # cae en bucket[0]
    metrics.add_histogram_value("response_time", 0.6)   # cae en bucket[2] => [0.1, 0.5, 1.0], [0.6 > 0.5 y <=1.0]
    metrics.add_histogram_value("response_time", 2.0)   # excede último => va al 'final'

    result = metrics.get_all_metrics()
    h = result["histograms"]["response_time"]
    # buckets=[0.1, 0.5, 1.0], counts => len=4 => [countBucket0, countBucket1, countBucket2, countOverflow]
    assert h["counts"] == [1, 0, 1, 1]
    assert h["sum"] == pytest.approx(2.65)
    assert h["total_count"] == 3

def test_decorator_measure_performance():
    metrics.init_metrics_system()
    @metrics.measure_performance("test_function_latency")
    def dummy_function(x):
        time.sleep(0.01)
        return x + 1

    res = dummy_function(5)
    assert res == 6

    mdata = metrics.get_all_metrics()
    # Se debe haber creado un histograma "test_function_latency" con 1 conteo
    histo = mdata["histograms"]["test_function_latency"]
    assert histo["total_count"] == 1
    assert histo["sum"] > 0.0

def test_concurrent_access():
    metrics.init_metrics_system()
    metrics.register_counter("hits")

    def worker():
        for _ in range(1000):
            metrics.inc("hits")

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    data = metrics.get_all_metrics()
    # 5 hilos * 1000 increments = 5000
    assert data["counters"]["hits"] == 5000

def test_record_time():
    metrics.init_metrics_system()
    start = time.time()
    time.sleep(0.02)
    elapsed = time.time() - start
    metrics.record_time("custom_time_metric", elapsed)
    data = metrics.get_all_metrics()
    hist = data["histograms"]["custom_time_metric"]
    assert hist["total_count"] == 1
    assert hist["sum"] == pytest.approx(elapsed, rel=1e-4)  # algo de tolerancia
