"""
monitor.py – Dashboard de Monitoreo y Administración en Tiempo Real

Este módulo implementa un panel de monitoreo basado en FastAPI y websockets.
Características avanzadas:
  - Streaming en tiempo real de logs y métricas.
  - Endpoints REST para obtener datos históricos.
  - Integración con el sistema de logging centralizado y el módulo de métricas.
  - Filtros y búsqueda dinámica de logs.
  
Este dashboard está diseñado para desplegarse en producción y conectarse tanto a un
frontend moderno (por ejemplo, desarrollado en Electron o un SPA) como para pruebas rápidas
desde un navegador.
"""

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from typing import List

# Se asume que utils/logger.py ya tiene un logger configurado globalmente.
from utils.logger import logger

app = FastAPI(title="Dashboard de Monitoreo RAG", version="2.0 Ultra-Extendida")
router = APIRouter()

# Almacenamiento en memoria (simulado) de logs y métricas históricos.
# En producción, esto podría estar respaldado por una base de datos o un motor de series temporales.
historical_logs: List[dict] = []
historical_metrics: List[dict] = []

# Lista de conexiones activas para websockets
active_connections: List[WebSocket] = []

# Simulación de fuente de métricas (en un caso real se integrarían con Prometheus, Graphite, etc.)
async def metrics_collector():
    """Simula la recolección periódica de métricas y las envía a los clientes conectados."""
    while True:
        # Ejemplo de métrica: tiempos de respuesta, uso de CPU, etc.
        metric = {
            "timestamp": asyncio.get_event_loop().time(),
            "response_time": 120,  # Valor simulado
            "cpu_usage": 55  # Valor simulado (%)
        }
        historical_metrics.append(metric)
        await broadcast(json.dumps({"type": "metric", "data": metric}))
        await asyncio.sleep(5)  # Recolecta métricas cada 5 segundos

async def broadcast(message: str):
    """Envía el mensaje a todas las conexiones activas."""
    remove_list = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"Error al enviar mensaje por websocket: {e}")
            remove_list.append(connection)
    for r in remove_list:
        active_connections.remove(r)

@router.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Esperar mensajes del cliente (por ejemplo, solicitudes de filtrado)
            data = await websocket.receive_text()
            # En un caso real, se procesaría el mensaje para ajustar la vista o filtrar logs
            logger.info(f"Mensaje recibido del cliente: {data}")
            # Se reenvía un acuse de recibo
            await websocket.send_text(json.dumps({"type": "ack", "data": data}))
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("Cliente desconectado del websocket.")

@router.get("/logs", response_class=JSONResponse)
async def get_logs(request: Request):
    """
    Endpoint para obtener logs históricos.
    Se pueden agregar parámetros de filtrado (por fecha, nivel, etc.) en el query string.
    """
    # Para ejemplo, se retorna todo el histórico.
    return {"logs": historical_logs}

@router.get("/metrics", response_class=JSONResponse)
async def get_metrics(request: Request):
    """
    Endpoint para obtener métricas históricas.
    """
    return {"metrics": historical_metrics}

# Endpoint HTML para visualizar el dashboard de forma sencilla.
@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Dashboard RAG</title>
    </head>
    <body>
      <h1>Dashboard de Monitoreo RAG</h1>
      <div id="logs"></div>
      <div id="metrics"></div>
      <script>
        var ws = new WebSocket("ws://" + location.host + "/ws/monitor");
        ws.onmessage = function(event) {
          var data = JSON.parse(event.data);
          if(data.type === "metric") {
            document.getElementById("metrics").innerText = "Métricas: " + JSON.stringify(data.data);
          } else if(data.type === "ack") {
            console.log("Acuse del servidor: " + data.data);
          }
        };
      </script>
    </body>
    </html>
    """
    return html_content

# Iniciar la tarea de métricas al arrancar la aplicación
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(metrics_collector())

app.include_router(router)
