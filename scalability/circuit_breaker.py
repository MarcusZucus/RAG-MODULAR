"""
circuit_breaker.py – Módulo de Tolerancia a Fallos y Escalabilidad

Este módulo implementa un Circuit Breaker avanzado que:
- Monitorea las llamadas a servicios externos.
- Permite definir un umbral de fallos para "abrir" el circuito.
- Utiliza un backoff exponencial en los reintentos.
- Permite la transición de estado de "cerrado" a "abierto" y luego a "semiabierto" para probar la recuperación.
- Registra métricas y eventos críticos a través del logger.

Características avanzadas:
- Parámetros configurables: failure_threshold, recovery_timeout, success_threshold, y backoff_factor.
- Integración con métricas y logging.
- Listo para producción en entornos asíncronos o síncronos.
"""

import time
import threading
import logging

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

class CircuitBreakerState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0,
                 success_threshold: int = 2, backoff_factor: float = 2.0):
        """
        Inicializa el Circuit Breaker.

        Args:
            failure_threshold (int): Número de fallos consecutivos antes de abrir el circuito.
            recovery_timeout (float): Tiempo (en segundos) de espera antes de pasar a estado semiabierto.
            success_threshold (int): Número de llamadas exitosas en estado semiabierto para cerrar el circuito.
            backoff_factor (float): Factor multiplicativo para incrementar el tiempo de espera en cada fallo.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.backoff_factor = backoff_factor

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        """
        Ejecuta la función protegida por el Circuit Breaker.

        Si el circuito está abierto, se lanza un RuntimeError inmediatamente.
        Si está semiabierto, se permite un número limitado de llamadas para evaluar la recuperación.

        Args:
            func: Función a ejecutar.
            args, kwargs: Argumentos a pasar a la función.

        Returns:
            El resultado de la función si es exitosa.

        Raises:
            RuntimeError: Si el circuito está abierto o si se exceden los reintentos.
        """
        with self.lock:
            current_time = time.time()
            if self.state == CircuitBreakerState.OPEN:
                if self.last_failure_time and (current_time - self.last_failure_time) >= self.recovery_timeout:
                    # Pasamos a semiabierto para probar la recuperación
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit Breaker: Transición a estado HALF_OPEN")
                else:
                    logger.error("Circuit Breaker: Circuito abierto, evitando ejecución")
                    raise RuntimeError("Circuit Breaker abierto. Servicio no disponible.")

        # Intentar la ejecución con reintentos y backoff exponencial
        attempt = 0
        delay = 1.0
        while attempt <= self.failure_threshold:
            try:
                result = func(*args, **kwargs)
                with self.lock:
                    if self.state == CircuitBreakerState.HALF_OPEN:
                        self.success_count += 1
                        if self.success_count >= self.success_threshold:
                            # Recuperación exitosa, cerrar el circuito
                            self._reset()
                            logger.info("Circuit Breaker: Recuperación exitosa, circuito cerrado")
                    else:
                        # En estado cerrado, resetear el contador de fallos si hay éxito
                        self.failure_count = 0
                return result
            except Exception as e:
                attempt += 1
                with self.lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    logger.error(f"Circuit Breaker: Error en la llamada (intento {attempt}): {e}")
                    # Si estamos en estado HALF_OPEN, cualquier fallo reabre el circuito
                    if self.state == CircuitBreakerState.HALF_OPEN:
                        self._trip()
                        raise RuntimeError("Circuit Breaker: Fallo en estado HALF_OPEN, circuito reabierto.") from e
                    # Si se excede el umbral, abrir el circuito
                    if self.failure_count >= self.failure_threshold:
                        self._trip()
                        raise RuntimeError("Circuit Breaker: Umbral de fallos excedido, circuito abierto.") from e
                time.sleep(delay)
                delay *= self.backoff_factor
        # Si se terminan los intentos sin éxito
        raise RuntimeError("Circuit Breaker: No se pudo completar la operación tras múltiples intentos.")

    def _trip(self):
        """Abre el circuito y resetea contadores."""
        self.state = CircuitBreakerState.OPEN
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = time.time()
        logger.error("Circuit Breaker: Circuito abierto.")

    def _reset(self):
        """Cierra el circuito y resetea todos los contadores."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info("Circuit Breaker: Circuito cerrado.")

# Ejemplo de uso directo:
if __name__ == "__main__":
    def test_service(x):
        # Función de ejemplo que falla si x es menor a 0
        if x < 0:
            raise ValueError("x no puede ser negativo")
        return x * 2

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5, success_threshold=2)
    try:
        print("Resultado:", breaker.call(test_service, -1))
    except Exception as e:
        print("Error:", e)
