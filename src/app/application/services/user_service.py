from app.api.v1.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from app.application.ports.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password
from app.domain.models.user import User
from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from datetime import datetime, timezone
from uuid import UUID


class UserService:
    def __init__(self, user_repo: UserRepository, logger):
        self.user_repo = user_repo
        self.logger = logger

    
    async def register_user(self, user_in: UserCreate) -> User:
        """
        Registra un nuevo usuario:
        1. Comprobar que el usuario no exista
        2. Hashear password
        3. Crear Entidad
        4. Persistir
        """
        self.logger.info(f"Se va a crear el usuario {user_in.username}")

        # 1. Regla de negocio: Email único
        if await self.user_repo.get_by_email(user_in.email):
            raise UserAlreadyExistsError("El email ya existe.")
        
        # 2. Hashear la contraseña
        hashed_password = get_password_hash(user_in.password)

        # 3. Construcción de la Entidad de Dominio
        new_user = User(
            username = user_in.username,
            email = user_in.email,
            password_hash = hashed_password,
            is_active = True,
            is_superuser = False
        )

        # 4. Persistencia
        try:
            new_user = await self.user_repo.create(new_user)
            self.logger.info(f"Usuario {user_in.username} creado correctamente.")
            return new_user
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def authenticate(self, identifier: str, password: str) -> User | None:
        user = await self.user_repo.get_by_identifier(identifier)

        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            return None
        
        return user


    async def get_user(self, user_id: UUID) -> User:
        """
        Obtiene un usuario por ID.
        """
        self.logger.info(f"Se va a obtener el usuario con ID {user_id}")

        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"El usuario con ID {user_id} no existe.")
            return user
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def get_user_by_email(self, email: str) -> User:
        """
        Obtiene un usuario por email.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"El usuario {email} no existe.")
        

    async def update_user(self, user_id: UUID, user_in: UserUpdate) -> User:
        """
        Permite al usuario cmabiar información de su perfil.
        No permite cambiar la contraseña (por seguridad).
        """
        user = await self.get_user(user_id)

        # TODO la modificación de is_active estará restringida solo a admins en el Endpoint
        has_changed = user.update_details(
            email = user_in.email,
            username = user_in.username,
            is_active = user.is_active
        )

        if not has_changed:
            return user
        
        return await self.user_repo.update(user)
    

    async def change_password(self, user_id: UUID, pass_in: UserPasswordUpdate) -> User:
        """
        Cambio seguro de contraseña.
        Verifica la actual antes de cambiar.
        """
        user = await self.get_user(user_id)

        if not verify_password(pass_in.current_password, user.password_hash):
            raise ValueError("La contraseña actual es incorrecta.")

        # Evitar reutilizar la misma contraseña
        if verify_password(pass_in.new_password, user.password_hash):
            raise ValueError("La nueva contraseña no puede ser igual a la actual.")
        
        user.password_hash = get_password_hash(pass_in.new_password)
        user.updated_at = datetime.now(timezone.utc)
        
        return await self.user_repo.update(user)

    
    async def delete_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)
        user.delete()
        return await self.user_repo.update(user)
