"""
ask.py – Endpoint /ask para Consultas del Usuario

Este módulo define un router de FastAPI que expone el endpoint /ask. Recibe una consulta en formato JSON,
invoca el pipeline RAG para procesarla y devuelve una respuesta estructurada.

Características avanzadas:
- Validación de entrada usando Pydantic.
- Manejo robusto de errores y conversión a HTTPException.
- Registro detallado de la solicitud y respuesta.
- Integración dinámica con el pipeline RAG (importado desde core.pipeline) para que se pueda hacer patch en tests.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

# Importamos la clase RAGPipeline desde core.pipeline
from core.pipeline import RAGPipeline

logger = logging.getLogger("RAGLogger")

router = APIRouter(
    prefix="/ask",
    tags=["ask"]
)

# Modelo para validar la solicitud
class AskRequest(BaseModel):
    query: str = Field(..., example="Hola, ¿cómo estás?")

# Modelo para la respuesta
class AskResponse(BaseModel):
    response: str

@router.post("/", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    Endpoint que procesa la consulta del usuario mediante el pipeline RAG.
    Retorna la respuesta generada o lanza un HTTPException en caso de error.
    """
    try:
        pipeline = RAGPipeline()
        result = pipeline.run(request.query)
        return AskResponse(response=result)
    except Exception as e:
        logger.error(f"Error en el endpoint /ask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno en el procesamiento de la consulta."
        )
