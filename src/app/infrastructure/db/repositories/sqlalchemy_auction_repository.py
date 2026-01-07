from app.domain.models.auction import Auction, Bid
from app.infrastructure.db.models.auction_orm import AuctionORM
from app.application.ports.auction_repository import AuctionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class SQLAlchemyAuctionRepository(AuctionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, auction_id: UUID) -> Auction | None:

        # 1. Crear la sentencia SELECT
        stmt = (
            select(AuctionORM)
            .where(AuctionORM.id == auction_id)
            .options(selectinload(AuctionORM.bids))
        )
        # 2. Ejecutar la consulta
        result = await self.session.execute(stmt)

        auction_orm = result.scalar_one_or_none()

        if not auction_orm:
            return None

        return Auction(
            id = auction_orm.id,
            title = auction_orm.title,
            starting_price = auction_orm.starting_price,
            start_time = auction_orm.start_time,
            end_time = auction_orm.end_time,
            bids = [
                Bid(
                    id = b.id,
                    bidder_id = b.bidder_id,
                    amount = b.amount,
                    created_at = b.created_at
                )
                for b in auction_orm.bids
            ]
        )


    async def save(self, auction: Auction) -> Auction:
        
        # 1. Mapear el objeto a insertar
        new_auction_orm = AuctionORM(
            id = auction.id,
            title = auction.title,
            starting_price = auction.starting_price,
            start_time = auction.start_time,
            end_time = auction.end_time,
            deleted_at = auction.deleted_at,
            seller_id = auction.seller_id
        )

        self.session.add(new_auction_orm)

        try:
            await self.session.commit()
            return auction
        except Exception as e:
            await self.session.rollback()
            raise e


    async def update(self, auction: Auction) -> Auction:
        pass
