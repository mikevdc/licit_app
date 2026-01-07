from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.base import get_session
from app.application.ports.auction_repository import AuctionRepository
from app.application.services.auction_service import AuctionService
from app.core.logging_setup import get_logger
from app.infrastructure.db.repositories.sqlalchemy_auction_repository import SQLAlchemyAuctionRepository


async def get_auction_repository(
        session: AsyncSession = Depends(get_session)
) -> AuctionRepository:
    return SQLAlchemyAuctionRepository(session)


async def get_auction_service(
        repo: AuctionRepository = Depends(get_auction_repository)
) -> AuctionService:
    auction_logger = get_logger("auctions")
    return AuctionService(repo, auction_logger)
