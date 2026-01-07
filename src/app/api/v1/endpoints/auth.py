from app.api.dependencies.users import get_user_repository
from app.api.v1.schemas.token import Token
from app.application.ports.user_repository import UserRepository
from app.core.security import create_access_token, verify_password
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix = "/auth")

@router.post("/login", response_model = Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_user_repository)
):
    user = await user_repo.get_by_identifier(form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Usuario o contraseña incorrectos",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject = user.id)
    return {"access_token": access_token, "token_type": "bearer"}
