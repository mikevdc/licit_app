from app.application.ports.user_repository import UserRepository
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


    def _to_domain(self, user_orm: UserORM) -> User | None:
        if not user_orm:
            return None
        
        return User(
            id = user_orm.id,
            username = user_orm.username,
            email = user_orm.email,
            password_hash = user_orm.password_hash,
            is_active = user_orm.is_active,
            created_at = user_orm.created_at
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


    async def get_by_identifier(self, identifier: str) -> User | None:
        """Busca un usuario por email o por username."""
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

        return self._to_domain(user_orm)


    async def get_by_id(self, user_id: UUID) -> User | None:

        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
        )
        result = await self.session.execute(stmt)

        user_orm = result.scalar_one_or_none()

        return self._to_domain(user_orm)
        
        
    async def get_by_email(self, email: str) -> User | None:

        stmt = (
            select(UserORM)
            .where(UserORM.email == email)
        )
        result = await self.session.execute(stmt)

        user_orm = result.scalar_one_or_none()

        return self._to_domain(user_orm)
    

    async def save(self, user: User) -> User:

        """
        Implementación robusta de Upsert (Update or Insert).
        1. Busca si el usuario ya existe en la DB (o en la Identity Map de la sesión).
        2. Si existe, actualiza los campos.
        3. Si no existe, crea una instancia nueva.
        """
        # Intentamos recuperar el objeto ORM actual asociado al este ID
        stmt = (
            select(UserORM)
            .where(UserORM.id == user.id)
        )
        result = await self.session.execute(stmt)
        existing_user_orm = result.scalar_one_or_none()

        if existing_user_orm:
            # Caso UPDATE
            # Trabajamos sobre la instancia viva de la sesión
            self._update_orm_from_domain(existing_user_orm, user)
            # No es necesario session.add(), SQLAlchemy ya lo está vigilando
        else:
            # Caso INSERT
            # Creamos una instancia nueva desde cero
            new_user_orm = UserORM(
                id = user.id,
                username = user.username,
                email = user.email,
                password_hash = user.password_hash,
                is_active = user.is_active,
                created_at = user.created_at
            )
            self.session.add(new_user_orm)

            try:
                # Flush envío los cambios a la DB pero no cierra la transacción
                await self.session.flush()
                await self.session.commit()

                # Refrescamos para obtener datos de vuelta
                await self.session.refresh(new_user_orm)

                return self._to_domain(new_user_orm)
            
            except IntegrityError as e:
                await self.session.rollback()
                if "Duplicate" in str(e.orig) or "unique" in str(e.orig).lower():
                    raise ValueError(f"El usuario ya existe.")
                raise e
