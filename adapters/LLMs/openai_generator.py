"""
openai_generator.py – Adaptador para Generación de Respuestas vía API de OpenAI

Este módulo se encarga de conectar con la API de OpenAI para generar respuestas a partir de un prompt.
Utiliza la API ChatCompletion (por ejemplo, gpt-3.5-turbo) y está diseñado para funcionar en entornos
de producción con manejo de errores, reintentos y registro avanzado.

Características:
- Validación de la API Key y configuración segura.
- Soporte para parámetros configurables: modelo, temperatura, número máximo de tokens, etc.
- Implementación de reintentos con backoff exponencial en caso de errores transitorios.
- Manejo robusto de excepciones específicas (RateLimitError, APIError, etc.) de la librería openai.
- Registro detallado de cada paso para facilitar la trazabilidad y el monitoreo.
"""

import os
import time
import logging
import openai
from openai.error import RateLimitError, APIError, Timeout, ServiceUnavailableError

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

def generate(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 150,
    retries: int = 3,
    backoff_factor: float = 2.0,
    **kwargs
) -> str:
    """
    Genera una respuesta a partir de un prompt utilizando la API de OpenAI.
    
    Args:
        prompt (str): El prompt de entrada.
        model (str): Modelo de lenguaje a utilizar. Por defecto "gpt-3.5-turbo".
        temperature (float): Parámetro de aleatoriedad de la generación.
        max_tokens (int): Número máximo de tokens en la respuesta.
        retries (int): Número de reintentos en caso de error.
        backoff_factor (float): Factor de tiempo para aumentar el retraso entre reintentos.
        kwargs: Parámetros adicionales que se pasan a la API de OpenAI.
    
    Returns:
        str: La respuesta generada.
    
    Raises:
        RuntimeError: Si la API Key no está configurada o si ocurren errores críticos en la generación.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY no está configurada.")
        raise RuntimeError("OPENAI_API_KEY no está configurada.")

    openai.api_key = openai_api_key

    # Configuración de la solicitud
    request_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }

    attempt = 0
    delay = 1  # segundos iniciales
    while attempt <= retries:
        try:
            logger.info(f"Enviando prompt a OpenAI (intento {attempt + 1}/{retries + 1})")
            response = openai.ChatCompletion.create(**request_payload)
            # Se espera que la respuesta tenga al menos un mensaje en choices
            if response and response.choices and len(response.choices) > 0:
                generated_text = response.choices[0].message.get("content", "").strip()
                logger.info("Respuesta generada exitosamente.")
                return generated_text
            else:
                logger.error("Respuesta inesperada: estructura de respuesta no válida.")
                raise RuntimeError("Respuesta inesperada de OpenAI.")
        except (RateLimitError, Timeout, ServiceUnavailableError) as transient_error:
            # Errores transitorios que se pueden reintentar
            logger.warning(f"Error transitorio al generar respuesta: {transient_error}. Reintentando en {delay} segundos...")
            time.sleep(delay)
            attempt += 1
            delay *= backoff_factor
        except APIError as api_error:
            logger.error(f"APIError: {api_error}")
            raise RuntimeError(f"Error en la API de OpenAI: {api_error}") from api_error
        except Exception as e:
            logger.error(f"Error inesperado al generar respuesta: {e}")
            raise RuntimeError(f"Error inesperado al generar respuesta: {e}") from e

    logger.error("Se agotaron los reintentos para generar la respuesta.")
    raise RuntimeError("No se pudo generar la respuesta después de múltiples intentos.")
