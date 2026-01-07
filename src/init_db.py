import asyncio
import logging

# 1. Configuración básica de logs para ver qué pasa
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("DB_INIT")

# 2. Importar la configuración de la DB
from app.infrastructure.db.session import engine
from app.infrastructure.db.base import Base

# 3. Importaciones obligatorias de modelos
# Aunque tengamos __init__.py, aquí prefiero ser explícito
# Si no se importa esto, las tablas no se crean
from app.infrastructure.db.models.user_orm import UserORM
from app.infrastructure.db.models.auction_orm import AuctionORM
from app.infrastructure.db.models.bid_orm import BidORM


async def init_db():
    logger.info("⌛ Iniciando la creación de tablas en la Base de Datos...")

    try:
        async with engine.begin() as conn:
            # Opcional: Descomentar esto si se quiere BORRAR todo y empezar de cero
            # logger.warning("⚠️ Borrando tablas existentes...")
            # await conn.run_sync(Base.metadata.drop_all)

            logger.info("🛠️ Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ ¡Éxito! Tablas creadas: Users, Auctions, Bids.")
    
    except Exception as e:
        logger.error(f"❌ Error crítico creando la base de datos: {e}")
        if "Connection refused" in str(e):
            logger.error("💡 Pista: ¿Está el contenedor de Docker levantado? (docker ps)")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
