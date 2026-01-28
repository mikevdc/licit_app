import jwt

from app.core.config import settings
from app.api.dependencies.users import get_user_repository
from app.api.v1.schemas.token import TokenPayload
from app.application.ports.user_repository import UserRepository
from app.domain.exceptions import UserInactiveError
from app.domain.models.user import User
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError, InvalidTokenError
from pydantic import ValidationError
from typing import Annotated
from uuid import UUID


"""
Ponemos el argumento tokenURL por SwaggerUI, no se usaría con un formulario real.
Esto hace que SwaggerUI muestre un formulario y envíe su información a esta url, para conseguir el 
token.
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> User:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No se pudieron validar las credenciales",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise credentials_exception
        
        token_data = TokenPayload(**payload)

        if not token_data.sub:
            raise credentials_exception
    
    except (PyJWTError, ValidationError, InvalidTokenError):
        # Capturamos tanto errores de firma (JWT) como de estructura (Pydantic)
        raise credentials_exception
    
    # Usamos el repositorio para buscar al usuario
    user_id_uuid = UUID(token_data.sub)
    user = await user_repo.get_by_id(user_id_uuid)

    if not user:
        raise credentials_exception
    
    if not user.is_active:
        raise UserInactiveError("Usuario inactivo.")
    
    return user
