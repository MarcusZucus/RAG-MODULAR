# api/routes/health.py

import asyncio
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict

from core.config import get_config
from core.service_detector import check_service_availability
from utils.logger import logger

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

class HealthStatus(BaseModel):
    service: str
    status: str
    detail: str = ""

class OverallHealth(BaseModel):
    overall_status: str
    checks: List[HealthStatus]

@router.get("/", response_model=OverallHealth)
async def health_check():
    """
    Endpoint para verificar el estado global de servicios críticos del sistema RAG.
    
    - Verifica variables de entorno y servicios externos con core/service_detector.
    - Comprueba si la configuración global se ha cargado adecuadamente.
    - Puede extenderse para medir tiempos de respuesta en DB, colas, etc.
    """
    logger.info("Iniciando chequeo de salud del sistema...")

    config = get_config()
    checks = []

    # Chequeo #1: Disponibilidad de base de datos
    db_available = check_service_availability("db")
    checks.append(HealthStatus(
        service="database",
        status="UP" if db_available else "DOWN",
        detail="DB_CONNECTION detectado" if db_available else "No config. o conexión DB"
    ))

    # Chequeo #2: Disponibilidad de OpenAI
    openai_available = check_service_availability("openai")
    checks.append(HealthStatus(
        service="openai_api",
        status="UP" if openai_available else "DOWN",
        detail="OPENAI_API_KEY configurada" if openai_available else "Falta la API key"
    ))

    # Chequeo #3: Revisión de adaptadores básicos (input, embedder, vector_store, llm)
    critical_adapters = ["input", "embedder", "vector_store", "llm"]
    for adapter_name in critical_adapters:
        adapter_value = getattr(config, adapter_name, None)
        # Verificar un presence check o la disponibilidad
        detail_msg = f"config.{adapter_name}={adapter_value}"
        checks.append(HealthStatus(
            service=f"{adapter_name}_adapter",
            status="UP" if adapter_value else "DOWN",
            detail=detail_msg
        ))

    # Construir respuesta global
    all_up = all(h.status == "UP" for h in checks)
    overall = "UP" if all_up else "DEGRADED"

    # Ejemplo: Podrías añadir “DOWN” total si ciertos servicios son imprescindibles
    if not db_available and not openai_available:
        overall = "DOWN"

    logger.info(f"Estado general de salud: {overall}")

    return OverallHealth(
        overall_status=overall,
        checks=checks
    )
