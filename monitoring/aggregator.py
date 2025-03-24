"""
aggregator.py – Módulo de Agregación de Logs y Métricas

Este módulo:
  - Centraliza la recolección de logs y métricas provenientes de diferentes módulos (API, pipeline, adaptadores, etc.).
  - Permite la configuración de umbrales y alertas.
  - Expone funciones para consultar datos en tiempo real.
  - Puede integrarse con un sistema de almacenamiento persistente (BD, ELK Stack, etc.).

Referencias (aggregator_README.md):
  - Recolección/centralización de logs y métricas.
  - Integración con monitoreo externo (Prometheus, Grafana, etc.).
  - Exposición de datos para consultas.
  - Configuración y activación de alertas.
  - Uso opcional de core/service_detector.py.

En esta versión "state-of-the-art", hemos incluido un sistema de alertas simulado, 
configurable y extensible para producción.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable

# Se asume que utils/logger.py ya está presente.
from utils.logger import logger

# Estructuras de almacenamiento en memoria (pueden ser reemplazadas por BD o colas)
LOGS_STORAGE: List[Dict[str, Any]] = []
METRICS_STORAGE: List[Dict[str, Any]] = []

# Lista de alertas configuradas: cada alerta se define como un dict con keys:
#   "name": str, "threshold_func": Callable[[Dict[str, Any]], bool], "on_trigger": Callable[[Dict[str, Any]], None]
ALERTS = []

def record_log(level: str, message: str, module: str = "general", extra: Dict[str, Any] = None):
    """
    Almacena un log en la estructura interna LOGS_STORAGE y también hace un logger.info/error/etc. real.

    Args:
        level (str): Nivel del log (debug, info, warning, error, critical).
        message (str): Mensaje de log.
        module (str): Nombre del módulo origen.
        extra (Dict[str, Any]): Datos adicionales.
    """
    log_entry = {
        "timestamp": time.time(),
        "level": level.lower(),
        "message": message,
        "module": module,
        "extra": extra or {}
    }
    LOGS_STORAGE.append(log_entry)

    # Emite el log real según el nivel
    if level.lower() == "debug":
        logger.debug(f"[{module}] {message}")
    elif level.lower() == "info":
        logger.info(f"[{module}] {message}")
    elif level.lower() == "warning":
        logger.warning(f"[{module}] {message}")
    elif level.lower() == "error":
        logger.error(f"[{module}] {message}")
    else:
        logger.critical(f"[{module}] {message}")


def record_metric(name: str, value: float, module: str = "general", extra: Dict[str, Any] = None):
    """
    Almacena una métrica en la estructura interna METRICS_STORAGE y verifica las alertas.

    Args:
        name (str): Nombre de la métrica (e.g., "response_time").
        value (float): Valor numérico de la métrica.
        module (str): Módulo origen (por ejemplo, "pipeline").
        extra (Dict[str, Any]): Datos adicionales.
    """
    metric_entry = {
        "timestamp": time.time(),
        "name": name,
        "value": value,
        "module": module,
        "extra": extra or {}
    }
    METRICS_STORAGE.append(metric_entry)

    # Verificar si alguna alerta se dispara con esta métrica
    for alert in ALERTS:
        try:
            if alert["threshold_func"](metric_entry):
                # Llamamos al callback on_trigger
                alert["on_trigger"](metric_entry)
        except Exception as e:
            logger.error(f"Error evaluando alerta '{alert.get('name')}' con métrica {metric_entry}: {e}")


def get_logs(since: float = 0, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retorna los logs almacenados, opcionalmente filtrados por tiempo y nivel.

    Args:
        since (float): timestamp mínimo (Unix time) para filtrar.
        level (str): Filtrar por nivel (debug, info, warning, error, critical).

    Returns:
        List[Dict[str, Any]]: Lista de logs que cumplan los criterios.
    """
    result = []
    for log_entry in LOGS_STORAGE:
        if log_entry["timestamp"] >= since:
            if level is None or log_entry["level"] == level.lower():
                result.append(log_entry)
    return result


def get_metrics(since: float = 0, name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retorna las métricas almacenadas, opcionalmente filtradas por tiempo y nombre.

    Args:
        since (float): timestamp mínimo para filtrar.
        name (str): Filtrar por nombre de la métrica (por ejemplo, "response_time").

    Returns:
        List[Dict[str, Any]]: Lista de métricas que cumplan los criterios.
    """
    result = []
    for metric in METRICS_STORAGE:
        if metric["timestamp"] >= since:
            if name is None or metric["name"] == name:
                result.append(metric)
    return result


def define_alert(name: str, threshold_func: Callable[[Dict[str, Any]], bool], on_trigger: Callable[[Dict[str, Any]], None]):
    """
    Define o registra una nueva alerta.

    Args:
        name (str): Nombre o identificador de la alerta.
        threshold_func (callable): Función que recibe una métrica y retorna True si se dispara la alerta.
        on_trigger (callable): Función callback que se llama cuando la alerta se activa.
    """
    alert_def = {
        "name": name,
        "threshold_func": threshold_func,
        "on_trigger": on_trigger
    }
    ALERTS.append(alert_def)
    logger.info(f"Alerta registrada: {name}")


def clear_alerts():
    """
    Elimina todas las alertas registradas.
    """
    ALERTS.clear()
    logger.info("Todas las alertas han sido eliminadas.")


def clear_data():
    """
    Limpia el almacenamiento interno de logs y métricas.
    """
    LOGS_STORAGE.clear()
    METRICS_STORAGE.clear()
    logger.info("Se han limpiado logs y métricas en el aggregator.")
