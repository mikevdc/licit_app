from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator


engine = create_async_engine(
    settings.DATABASE_URL, 
    echo = False
)

AsyncSessionLocal = async_sessionmaker(bind = engine, class_ = AsyncSession, expire_on_commit = False)


async def get_db() -> AsyncGenerator[AsyncGenerator, None]:
    """
    Generador de dependencias para FastAPI.
    Crea una sesión nueva por request y la cierra al terminar.
    """
    async with AsyncSessionLocal() as session:
        yield session
