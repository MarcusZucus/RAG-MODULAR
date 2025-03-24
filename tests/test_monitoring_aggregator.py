"""
tests/test_monitoring_aggregator.py – Pruebas Unitarias para el módulo monitoring/aggregator.py.

Referencia: monitoring/aggregator_README.md.
- Se prueban la agregación de logs y métricas, la configuración de alertas y la exposición de datos.
"""

import time
import pytest
from monitoring import aggregator

@pytest.fixture(autouse=True)
def clean_aggregator():
    """
    Limpia el almacenamiento interno de aggregator antes y después de cada test.
    """
    aggregator.clear_data()
    aggregator.clear_alerts()
    yield
    aggregator.clear_data()
    aggregator.clear_alerts()

def test_record_log():
    aggregator.record_log("info", "Mensaje de prueba", module="test_module")
    logs = aggregator.get_logs()
    assert len(logs) == 1
    assert logs[0]["message"] == "Mensaje de prueba"
    assert logs[0]["level"] == "info"
    assert logs[0]["module"] == "test_module"

def test_get_logs_level_filter():
    aggregator.record_log("info", "Log info")
    aggregator.record_log("error", "Log error")
    info_logs = aggregator.get_logs(level="info")
    error_logs = aggregator.get_logs(level="error")

    assert len(info_logs) == 1
    assert info_logs[0]["message"] == "Log info"
    assert len(error_logs) == 1
    assert error_logs[0]["message"] == "Log error"

def test_get_logs_since():
    aggregator.record_log("info", "Old log")
    time.sleep(0.1)
    t_start = time.time()
    aggregator.record_log("info", "New log")
    filtered = aggregator.get_logs(since=t_start)
    assert len(filtered) == 1
    assert filtered[0]["message"] == "New log"

def test_record_metric():
    aggregator.record_metric("response_time", 123.45, module="api")
    metrics = aggregator.get_metrics()
    assert len(metrics) == 1
    assert metrics[0]["name"] == "response_time"
    assert metrics[0]["value"] == 123.45
    assert metrics[0]["module"] == "api"

def test_get_metrics_name_filter():
    aggregator.record_metric("response_time", 100)
    aggregator.record_metric("cpu_usage", 45)
    rt_metrics = aggregator.get_metrics(name="response_time")
    cpu_metrics = aggregator.get_metrics(name="cpu_usage")
    assert len(rt_metrics) == 1
    assert len(cpu_metrics) == 1

def test_alert_trigger():
    alert_triggered = []

    def threshold_func(metric):
        # Dispara la alerta si la métrica "cpu_usage" > 80
        return metric["name"] == "cpu_usage" and metric["value"] > 80

    def on_trigger(metric):
        alert_triggered.append(metric)

    aggregator.define_alert("High CPU", threshold_func, on_trigger)
    aggregator.record_metric("cpu_usage", 70)
    aggregator.record_metric("cpu_usage", 81)

    assert len(alert_triggered) == 1
    assert alert_triggered[0]["value"] == 81

def test_clear_data():
    aggregator.record_log("info", "Some log")
    aggregator.record_metric("requests", 10)
    aggregator.clear_data()
    assert len(aggregator.get_logs()) == 0
    assert len(aggregator.get_metrics()) == 0

def test_clear_alerts():
    aggregator.define_alert("Dummy Alert", lambda m: True, lambda m: None)
    assert len(aggregator.ALERTS) == 1
    aggregator.clear_alerts()
    assert len(aggregator.ALERTS) == 0
