import time
import pytest
from scalability.circuit_breaker import CircuitBreaker, CircuitBreakerState

# Función dummy que falla siempre
def always_fail(*args, **kwargs):
    raise Exception("Fallo simulado")

# Función dummy que siempre tiene éxito
def always_succeed(x):
    return x + 10

# Función dummy que falla algunas veces y luego tiene éxito
class FlakyService:
    def __init__(self, fail_times):
        self.fail_times = fail_times

    def __call__(self, x):
        if self.fail_times > 0:
            self.fail_times -= 1
            raise Exception("Fallo transitorio")
        return x + 10

def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2, success_threshold=1, backoff_factor=1)
    # Realizamos llamadas que fallan para superar el umbral
    with pytest.raises(RuntimeError, match="Umbral de fallos excedido"):
        for _ in range(4):
            breaker.call(always_fail)
    # Verificamos que el estado es OPEN
    assert breaker.state == CircuitBreakerState.OPEN

def test_circuit_breaker_recovery():
    # Inicialmente, el servicio falla dos veces, luego tiene éxito.
    flaky = FlakyService(fail_times=2)
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1, success_threshold=2, backoff_factor=1)
    # Se esperan fallos iniciales pero que no superen el umbral para abrir el circuito
    for _ in range(2):
        with pytest.raises(RuntimeError):
            breaker.call(flaky, 5)
    # Esperamos la expiración del recovery_timeout
    time.sleep(1.1)
    # Ahora estamos en HALF_OPEN; se deben realizar llamadas exitosas para cerrar el circuito
    result = breaker.call(always_succeed, 5)
    assert result == 15
    result = breaker.call(always_succeed, 5)
    assert result == 15
    # El circuito debería cerrarse tras suficientes éxitos
    assert breaker.state == CircuitBreakerState.CLOSED

def test_circuit_breaker_half_open_failure():
    # En estado HALF_OPEN, cualquier fallo debe reabrir el circuito.
    flaky = FlakyService(fail_times=0)
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1, success_threshold=2, backoff_factor=1)
    # Abrir el circuito manualmente simulando un fallo
    with breaker.lock:
        breaker.state = CircuitBreakerState.OPEN
        breaker.last_failure_time = time.time() - 1.1  # Forzar el paso a HALF_OPEN
    # Llamada que falla en HALF_OPEN debe reabrir el circuito
    with pytest.raises(RuntimeError, match="Fallo en estado HALF_OPEN"):
        breaker.call(always_fail)
    assert breaker.state == CircuitBreakerState.OPEN
