from app.application.ports.user_repository import UserRepository
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.models.user import User
from app.infrastructure.db.models.user_orm import UserORM
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    # --- MAPPERS ---
    def _to_orm(self, user: User) -> UserORM:
        """Dominio (@dataclass) -> BD (ORM)"""
        return UserORM(
            id = user.id,
            username = user.username,
            email = user.email,
            password_hash = user.password_hash,
            is_active = user.is_active,
            is_superuser = user.is_superuser,
            created_at = user.created_at,
            updated_at = user.updated_at,
            deleted_at = user.deleted_at
        )


    def _to_domain(self, user_orm: UserORM) -> User:
        """BD (ORM) -> Dominio (@dataclass)"""        
        return User(
            id = user_orm.id,
            username = user_orm.username,
            email = user_orm.email,
            password_hash = user_orm.password_hash,
            is_active = user_orm.is_active,
            is_superuser = user_orm.is_superuser,
            created_at = user_orm.created_at,
            updated_at = user_orm.updated_at,
            deleted_at = user_orm.deleted_at
        )
    
    
    def _update_orm_from_domain(self, user_orm: UserORM, user_domain: User) -> None:
        """
        Transfiere los datos del Dominio al objeto ORM **ya existente** y **atacheado**.
        Esto permite que SQLAlchemy detecte solo los campos que han cambiado (Dirty Checking).
        """
        user_orm.username = user_domain.username
        user_orm.email = user_domain.email
        user_orm.password_hash = user_domain.password_hash
        user_orm.is_active = user_domain.is_active
        user_orm.is_superuser = user_domain.is_superuser
        user_orm.updated_at = user_domain.updated_at
        user_orm.deleted_at = user_domain.deleted_at
    

    # --- IMPLEMENTACIÓN DE LA INTERFAZ ---
    async def create(self, user: User) -> User:
        user_orm = self._to_orm(user)
        try:
            self.session.add(user_orm)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise UserAlreadyExistsError(f"El usuario introducido ya existe.")
        
        return user
    

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
        )
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None
    

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(UserORM)
            .where(UserORM.email == email)
        )
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None
    

    async def get_by_identifier(self, identifier: str) -> User | None:
        stmt = (
            select(UserORM)
            .where(
                or_(
                    UserORM.email == identifier,
                    UserORM.username == identifier
                )
            )
        )
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None
        

    async def update(self, user: User) -> User:
        """Busca el usuario en la BD, actualiza sus campos y guarda."""
        stmt = (
            select(UserORM)
            .where(UserORM.id == user.id)
        )
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()

        if not user_orm:
            raise ValueError(f"Usuario {user.id} no encontrado para actualizar.")
        
        self._update_orm_from_domain(user_orm, user)
        await self.session.commit()
        return user
