import os
import time
import jwt
import pytest
from security import auth

# Asegurarse de establecer una secret_key de prueba
@pytest.fixture(autouse=True)
def set_test_secret_key(monkeypatch):
    monkeypatch.setenv("secret_key", "mi_super_secreto_de_prueba")
    yield
    monkeypatch.delenv("secret_key", raising=False)

def test_create_and_verify_token():
    payload = {"user_id": "usuario123", "role": "admin"}
    token = auth.create_token(payload, expiration=10)  # expiración corta para prueba
    # Verificar que el token es un string
    assert isinstance(token, str)
    
    # Decodificar y verificar el payload
    decoded = auth.verify_token(token)
    # El payload original debe estar presente (la firma "exp" se agrega adicionalmente)
    assert decoded.get("user_id") == "usuario123"
    assert decoded.get("role") == "admin"
    assert "exp" in decoded

def test_token_expiration(monkeypatch):
    payload = {"user_id": "usuario123"}
    # Crear un token con expiración de 1 segundo
    token = auth.create_token(payload, expiration=1)
    # Esperar 2 segundos para forzar la expiración
    time.sleep(2)
    with pytest.raises(RuntimeError, match="Token expirado"):
        auth.verify_token(token)

def test_invalid_token():
    # Probar con un token manipulado o inválido
    invalid_token = "token.invalido.xxx"
    with pytest.raises(RuntimeError, match="Token inválido"):
        auth.verify_token(invalid_token)

def test_missing_secret_key(monkeypatch):
    # Remover la secret_key y probar la generación y verificación
    monkeypatch.delenv("secret_key", raising=False)
    payload = {"user_id": "usuario123"}
    with pytest.raises(RuntimeError, match="Secret key no configurado"):
        auth.create_token(payload)
    # Para verificación, también se espera fallo
    with pytest.raises(RuntimeError, match="Secret key no configurado"):
        auth.verify_token("cualquier.token")
