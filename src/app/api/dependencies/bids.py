from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.base import get_session
from app.api.dependencies.auctions import get_auction_repository
from app.application.ports.auction_repository import AuctionRepository
from app.application.ports.bid_repository import BidRepository
from app.application.services.bid_service import BidService
from app.core.logging_setup import get_logger
from app.infrastructure.db.repositories.sqlalchemy_bid_repository import SQLAlchemyBidRepository


async def get_bid_repository(
        session: AsyncSession = Depends(get_session)
) -> BidRepository:
    return SQLAlchemyBidRepository(session)


async def get_bid_service(
        bid_repo: BidRepository = Depends(get_bid_repository),
        auction_repo: AuctionRepository = Depends(get_auction_repository)
) -> BidService:
    bid_logger = get_logger("bids")
    return BidService(bid_logger, bid_repo, auction_repo)
