from abc import ABC, abstractmethod
from app.domain.models.user import User
from uuid import UUID


class UserRepository(ABC):
    """
    Puerto de salida: Interfaz abstracta para la persistencia de usuarios.
    No sabe nada de SQLAlchemy, solo conoce modelos de dominio.
    """

    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> User | None:
        """Recupera un usuario por su ID único, o por su email."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Recupera un usuario por su ID único."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Recupera un usuario por su correo electrónico."""
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Persiste un nuevo usuario en el sistema."""
        raise NotImplementedError
