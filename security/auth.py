"""
auth.py – Módulo de Autenticación y Autorización

Este módulo implementa un sistema de autenticación robusto utilizando JWT (JSON Web Tokens).
Provee funciones para:
  - Generar tokens a partir de credenciales válidas.
  - Verificar y decodificar tokens para proteger endpoints críticos.
  
Se utiliza el secreto (secret_key) definido en la configuración (core/config.py o en .env)
para firmar y validar los tokens.
"""

import os
import time
import jwt  # Asegúrate de tener PyJWT instalado (pip install pyjwt)
from jwt import ExpiredSignatureError, InvalidTokenError
import logging

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

# Tiempo de expiración predeterminado en segundos (por ejemplo, 1 hora)
DEFAULT_EXPIRATION_SECONDS = 3600

def create_token(payload: dict, expiration: int = DEFAULT_EXPIRATION_SECONDS) -> str:
    """
    Genera un JWT firmado usando el secret_key del entorno.
    
    Args:
        payload (dict): Datos a incluir en el token (por ejemplo, identificador de usuario, roles, etc.).
        expiration (int): Tiempo en segundos hasta la expiración del token (default: 3600).
        
    Returns:
        str: Token JWT firmado.
    
    Raises:
        RuntimeError: Si no se encuentra el secret_key.
    """
    secret_key = os.getenv("secret_key")
    if not secret_key:
        logger.error("secret_key no está configurado en las variables de entorno.")
        raise RuntimeError("Secret key no configurado.")
    
    exp = int(time.time()) + expiration
    token_payload = {**payload, "exp": exp}
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")
    logger.info("Token generado exitosamente.")
    return token

def verify_token(token: str) -> dict:
    """
    Verifica y decodifica el token JWT.
    
    Args:
        token (str): Token JWT a verificar.
    
    Returns:
        dict: El payload decodificado si el token es válido.
    
    Raises:
        RuntimeError: Si el token ha expirado o es inválido.
    """
    secret_key = os.getenv("secret_key")
    if not secret_key:
        logger.error("secret_key no está configurado en las variables de entorno.")
        raise RuntimeError("Secret key no configurado.")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        logger.info("Token verificado exitosamente.")
        return payload
    except ExpiredSignatureError as e:
        logger.error("Token expirado.")
        raise RuntimeError("Token expirado.") from e
    except InvalidTokenError as e:
        logger.error("Token inválido.")
        raise RuntimeError("Token inválido.") from e
