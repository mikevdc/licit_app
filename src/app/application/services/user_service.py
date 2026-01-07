import uuid
from app.application.ports.user_repository import UserRepository
from app.core.security import get_password_hash
from app.domain.models.user import User
from app.domain.exceptions import UserNotFoundError
from datetime import datetime, timezone
from uuid import UUID


class UserService:
    def __init__(self, repository: UserRepository, logger):
        self.repository = repository
        self.logger = logger

    
    async def create_user(self, username: str, email: str, password: str) -> User:
        """
        Caso de Uso: Crear un nuevo usuario.
        """
        self.logger.info(f"Se va a crear el usuario {username}")

        # 1. Regla de negocio: Email único
        if await self.repository.get_by_email(email):
            raise ValueError("El email ya existe")
        
        # 2. Hashear la contraseña
        hashed_password = get_password_hash(password)

        # 3. Construcción de la Entidad de Dominio
        new_user = User(
            id = uuid.uuid4(),
            username = username,
            email = email,
            password_hash = hashed_password,
            is_active = True,
            created_at = datetime.now(timezone.utc)
        )

        # 4. Persistencia
        try:
            new_user = await self.repository.save(new_user)
            self.logger.info(f"Usuario {username} creado correctamente.")
            return new_user
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def get_user(self, user_id: UUID) -> User:
        """
        Caso de Uso: Obtener un usuario por ID.
        """
        self.logger.info(f"Se va a obtener el usuario con ID {user_id}")

        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"El usuario con ID {user_id} no existe.")
            return user
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e
