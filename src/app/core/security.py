import jwt

from app.core.config import settings
from datetime import datetime, timedelta, timezone
from typing import Any
from pwdlib import PasswordHash

# Configuración con Argon2 (recomendado por OWASP)
password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña usando pwdlib."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash Argon2."""
    return password_hash.hash(password)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Crea el JWT usando PyJWT."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Construimos el payload
    # PyJWT es estricto con los tipos: 'exp' debe ser numérico (timestamp)
    # Pero si pasas datetime con timezone, él lo gestiona
    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
    return encoded_jwt
