from app.api.dependencies.auth import get_current_user
from app.api.dependencies.users import get_user_service
from app.api.v1.schemas.user import UserCreate, UserResponse, UserUpdate, UserPasswordUpdate
from app.application.services.user_service import UserService
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated


router = APIRouter(prefix = "/users")

# Alias para dependencias
ServiceDep = Annotated[UserService, Depends(get_user_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

@ router.post("/", response_model = UserResponse, status_code = 201) # El 201 es el estándar para 'Created'
async def register_user(user_in: UserCreate, service: ServiceDep):
    try:
        return await service.register_user(user_in) # FastAPI convierte la Entidad de Dominio -> UserResponse automáticamente
    
    except UserAlreadyExistsError as e:
        # Capturamos errores de negocio lanzados por el Repo/Servicio
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = str(e))


@router.get("/me", response_model = UserResponse)
async def read_user_me(current_user: CurrentUserDep):
    return current_user


@router.patch("/me", response_model = UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: CurrentUserDep,
    service: ServiceDep
):
    try:
        return await service.update_user(current_user.id, user_in)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))


@router.post("/me/password")
async def change_password_me(
    pass_in: UserPasswordUpdate,
    current_user: CurrentUserDep,
    service: ServiceDep
):
    try:
        await service.change_password(current_user.id, pass_in)
        return {"msg": "Contraseña actualizada exitosamente."}
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))
    

@router.delete("/me", status_code = 204)
async def delete_user_me(current_user: CurrentUserDep, service: ServiceDep):
    await service.delete_user(current_user.id)
