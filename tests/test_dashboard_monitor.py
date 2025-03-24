import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from dashboard.monitor import app, active_connections, historical_logs, historical_metrics

client = TestClient(app)

@pytest.fixture
def run_event_loop():
    # Fixture para asegurar el loop de asyncio en los tests de websockets
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

def test_get_logs():
    # Simula la adición de logs históricos
    historical_logs.append({"timestamp": 123456, "level": "INFO", "message": "Test log"})
    response = client.get("/logs")
    data = response.json()
    assert response.status_code == 200
    assert "logs" in data
    assert len(data["logs"]) > 0

def test_get_metrics():
    # Simula la adición de métricas históricas
    historical_metrics.append({"timestamp": 123456, "response_time": 120, "cpu_usage": 55})
    response = client.get("/metrics")
    data = response.json()
    assert response.status_code == 200
    assert "metrics" in data
    assert len(data["metrics"]) > 0

@pytest.mark.asyncio
async def test_websocket_monitor():
    # Usa el cliente websocket de TestClient para conectarse y probar el endpoint
    with client.websocket_connect("/ws/monitor") as websocket:
        # Envía un mensaje y espera acuse de recibo
        test_message = "Filtrar: ERROR"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        response_data = json.loads(data)
        assert response_data.get("type") == "ack"
        assert response_data.get("data") == test_message

    # Después de desconectar, la conexión debe eliminarse de active_connections
    await asyncio.sleep(0.1)
    assert all(ws.closed for ws in active_connections) or len(active_connections) == 0
