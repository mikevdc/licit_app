from app.api.dependencies.users import get_user_service
from app.api.v1.schemas.token import Token
from app.application.services.user_service import UserService
from app.core.security import create_access_token, verify_password
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated


router = APIRouter(prefix = "/auth")

@router.post("/login", response_model = Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_repo: Annotated[UserService, Depends(get_user_service)]
):
    user = await user_repo.authenticate(
        identifier = form_data.username,
        password = form_data.password
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Usuario o contraseña incorrectos",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject = user.id)
    return {"access_token": access_token, "token_type": "bearer"}
