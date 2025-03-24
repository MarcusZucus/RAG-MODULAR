"""
api/app.py – Punto de Entrada de la API del Sistema RAG

Este script inicializa la aplicación FastAPI, configura middlewares (CORS, logging, autenticación),
registra los endpoints disponibles y expone la documentación interactiva.

Características avanzadas:
- Configuración de CORS para restringir orígenes (se puede ajustar según el entorno).
- Middleware para logging global de solicitudes y respuestas.
- Integración de un placeholder para autenticación (JWT/OAuth2) para producción.
- Registro dinámico de routers (ask, health, admin) desde la carpeta api/routes.
- Manejo global de excepciones para capturar errores inesperados.
"""

import os
import uvicorn
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configuración básica de logging para la API
logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Proyecto RAG – API",
    description="API para el sistema RAG con generación de respuestas, indexación y búsqueda semántica.",
    version="2.0 Ultra-Extendida",
)

# Configuración de CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Logging para cada request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Solicitud entrante: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Respuesta: status code {response.status_code}")
    return response

# Middleware de manejo global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado en el servidor."},
    )

# Placeholder para autenticación avanzada: en producción se integrará JWT/OAuth2
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Si la ruta requiere autenticación, se validaría el token
    # Aquí se puede verificar headers, cookies, etc.
    # Ejemplo: si no hay token en header y la ruta no es pública, rechazar.
    # Por ahora, se deja pasar todas las solicitudes.
    return await call_next(request)

# Registro dinámico de routers
def include_routes():
    """
    Incluye todos los routers disponibles en la carpeta api/routes.
    Se asume que cada archivo en api/routes define un objeto "router" de FastAPI.
    """
    from pathlib import Path
    import importlib.util

    routes_path = Path(__file__).parent / "routes"
    for route_file in routes_path.glob("*.py"):
        if route_file.name.startswith("__"):
            continue
        module_name = f"api.routes.{route_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, route_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "router"):
            app.include_router(module.router)
            logger.info(f"Incluido router: {module_name}")

include_routes()

# Punto de entrada cuando se ejecuta el script directamente.
if __name__ == "__main__":
    uvicorn.run("api.app:app", host=os.getenv("UVICORN_HOST", "0.0.0.0"), port=int(os.getenv("UVICORN_PORT", 8000)), reload=False)
