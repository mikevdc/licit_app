from app.api.dependencies.users import get_user_service
from app.api.v1.schemas.user import UserCreate, UserResponse
from app.application.services.user_service import UserService
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID


router = APIRouter(prefix = "/users")


@ router.post("/", status_code = 201, response_model = UserResponse) # El 201 es el estándar para 'Created'
async def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        new_user = await service.create_user(
            username = user_in.username,
            email = user_in.email,
            password = user_in.password
        )

        # FastAPI convierte la Entidad de Dominio -> UserResponse automáticamente
        return new_user
    
    except ValueError as e:
        # Capturamos errores de negocio lanzados por el Repo/Servicio
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))


@router.get("/{user_id}", response_model = UserResponse)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuario no encontrado")
    return user
