from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.base import get_session
from app.application.ports.user_repository import UserRepository
from app.application.services.user_service import UserService
from app.core.logging_setup import get_logger
from app.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


async def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_user_service(
        repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    user_logger = get_logger("users")
    return UserService(repo, user_logger)
