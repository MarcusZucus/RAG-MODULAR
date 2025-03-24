# api/routes/admin.py

import logging
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import List, Optional

from utils.logger import logger
from utils.cache_manager import clear_schema_cache
from monitoring.aggregator import get_logs, get_metrics, clear_data
from core.config import get_config, update_config

# from security.auth import verify_token  # Ejemplo de security, p.ej. con un "Bearer" token

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

class UpdateConfigRequest(BaseModel):
    search_k: Optional[int] = None
    api_key: Optional[str] = None
    # Puedes definir más campos que correspondan con config.py

@router.get("/logs")
def admin_get_logs(level: Optional[str] = None):
    """
    Retorna logs filtrados por nivel (info, error, warning, etc.)
    Ejemplo de uso: /admin/logs?level=error
    """
    results = get_logs(level=level)
    return {
        "count": len(results),
        "logs": results
    }

@router.get("/metrics")
def admin_get_metrics(name: Optional[str] = None):
    """
    Retorna métricas registradas en aggregator, filtradas opcionalmente por nombre.
    Ejemplo: /admin/metrics?name=cpu_usage
    """
    results = get_metrics(name=name)
    return {
        "count": len(results),
        "metrics": results
    }

@router.post("/config")
def admin_update_config(payload: UpdateConfigRequest):
    """
    Actualiza configuraciones críticas en caliente:
    - search_k
    - api_key (que internamente se remapea a openai_api_key)
    """
    logger.warning(f"Actualizando configuración vía API Admin: {payload}")
    changes = payload.dict(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay cambios que aplicar.")

    try:
        update_config(changes)
        return {
            "message": "Configuración actualizada",
            "new_config": get_config().model_dump()
        }
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/reset")
def admin_system_reset(full_reset: bool = Query(False, description="Si es True, se limpia todo: logs, caches, etc.")):
    """
    Ejecuta ciertas acciones críticas de reseteo/limpieza:
    - Limpieza de logs/metrics.
    - Limpieza de caché de esquemas u otras caches.

    Este tipo de endpoint debe protegerse por roles o tokens seguros.
    """
    if full_reset:
        clear_data()
        clear_schema_cache()
        logger.info("Se ejecutó un FULL RESET de data y cache de esquemas.")
        return {"message": "FULL RESET completado: logs, métricas y schema cache limpiados."}
    else:
        # Acciones parciales
        clear_data()
        logger.info("Se limpiaron logs y métricas, NO se tocó la schema cache.")
        return {"message": "Se limpiaron logs y métricas."}
