import jwt

from app.core.config import settings
from app.api.dependencies.users import get_user_repository
from app.api.v1.schemas.token import TokenPayload
from app.application.ports.user_repository import UserRepository
from app.infrastructure.db.models.user_orm import UserORM
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from pydantic import ValidationError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_user_repository)
) -> "UserORM":
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No se pudieron validar las credenciales",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])

        token_data = TokenPayload(**payload)

        if not token_data.sub:
            raise credentials_exception
    
    except (PyJWTError, ValidationError):
        # Capturamos tanto errores de firma (JWT) como de estructura (Pydantic)
        raise credentials_exception
    
    # Usamos el repositorio para buscar al usuario
    user = await user_repo.get_by_id(token_data.sub)

    if not user:
        raise credentials_exception
    
    return user
