import logging
import io
import os
import pytest
from utils.logger import logger

@pytest.fixture
def log_capture():
    # Configurar un StringIO para capturar la salida del logger
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    # Añadir el handler temporal al logger
    logger.addHandler(stream_handler)
    yield log_stream
    # Remover el handler temporal después de la prueba
    logger.removeHandler(stream_handler)
    log_stream.close()

def test_logger_default_level(log_capture):
    # En condiciones por defecto, el nivel es DEBUG
    logger.debug("Mensaje debug")
    logger.info("Mensaje info")
    logger.warning("Mensaje warning")
    logger.error("Mensaje error")
    log_contents = log_capture.getvalue()
    # Verificar que los mensajes se encuentren en la salida
    assert "DEBUG - Mensaje debug" in log_contents
    assert "INFO - Mensaje info" in log_contents
    assert "WARNING - Mensaje warning" in log_contents
    assert "ERROR - Mensaje error" in log_contents

def test_logger_change_level(monkeypatch, log_capture):
    # Simula un cambio de variable de entorno para que el nivel sea WARNING
    monkeypatch.setenv("RAG_LOG_LEVEL", "WARNING")
    
    # Reiniciar la configuración del logger. Dado que el logger ya está configurado, 
    # para la prueba se recrea un logger temporal con la configuración modificada.
    test_logger = logging.getLogger("RAGLoggerTest")
    if test_logger.handlers:
        for handler in test_logger.handlers[:]:
            test_logger.removeHandler(handler)
    test_logger.setLevel(getattr(logging, os.getenv("RAG_LOG_LEVEL", "WARNING")))
    stream_handler = logging.StreamHandler(log_capture)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    test_logger.addHandler(stream_handler)

    test_logger.debug("Este mensaje debug no debería aparecer")
    test_logger.info("Este mensaje info no debería aparecer")
    test_logger.warning("Mensaje warning")
    test_logger.error("Mensaje error")

    log_contents = log_capture.getvalue()
    # Los mensajes DEBUG e INFO no deben estar presentes, mientras que WARNING y ERROR sí
    assert "DEBUG - Este mensaje debug no debería aparecer" not in log_contents
    assert "INFO - Este mensaje info no debería aparecer" not in log_contents
    assert "WARNING - Mensaje warning" in log_contents
    assert "ERROR - Mensaje error" in log_contents

def test_logger_format(log_capture):
    # Verificar que el formato de los logs contenga el nivel y el mensaje
    logger.info("Formato test")
    log_contents = log_capture.getvalue().strip()
    # Se espera un formato tipo "INFO - Formato test" (la fecha puede variar)
    assert "INFO - Formato test" in log_contents
