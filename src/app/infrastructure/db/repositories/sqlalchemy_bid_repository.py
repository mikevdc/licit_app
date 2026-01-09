from app.domain.exceptions import AuctionError
from app.domain.models.auction import Auction, Bid
from app.infrastructure.db.models.auction_orm import AuctionORM, BidORM
from app.application.ports.bid_repository import BidRepository
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class SQLAlchemyBidRepository(BidRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    

    # --- MAPPERS ---
    def _to_orm(self, bid: Bid) -> BidORM:
        """Dominio (@dataclass) -> BD (ORM)"""
        return BidORM(
            id = bid.id,
            amount = bid.amount,
            created_at = bid.created_at,
            deleted_at = None, # Las pujas nuevas naces vivas
            auction_id = bid.auction_id,
            bidder_id = bid.bidder_id
        )
    

    def _to_domain(self, bid_orm: BidORM) -> Bid:
        """BD (ORM) -> Dominio (@dataclass)"""
        return Bid(
            id = bid_orm.id,
            amount = bid_orm.amount,
            created_at = bid_orm.created_at,
            deleted_at = bid_orm.deleted_at,
            auction_id = bid_orm.auction_id,
            bidder_id = bid_orm.bidder_id
        )
    

    # --- IMPLEMENTACIÓN DE LA INTERFAZ ---
    async def create(self, bid: Bid) -> Bid:
        bid_orm = self._to_orm(bid)
        try:
            self.sesion.add(bid_orm)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise AuctionError(f"No se pudo crear la puja. Verifica que la subasta {bid.auction_id} y el usuario {bid.bidder_id} existan.")
        
        return bid
    

    async def get_by_id(self, bid_id: UUID) -> Bid | None:
        stmt = (
            select(BidORM)
            .where(BidORM.id == bid_id)
        )
        result = await self.session.execute(stmt)
        bid_orm = result.scalar_one_or_none()
        return self._to_domain(bid_orm) if bid_orm else None
    

    async def get_by_auction_id(self, auction_id: UUID) -> list[Bid]:
        stmt = (
            select(BidORM)
            .where(BidORM.auction_id == auction_id)
            .order_by(BidORM.amount.desc()) # Ordenamos la más alta primero
        )
        result = await self.session.execute(stmt)
        bids_orm = result.scalars().all()

        return [self._to_domain(b) for b in bids_orm]


    async def delete(self, bid_id: UUID) -> bool:
        stmt = (
            select(BidORM)
            .where(BidORM.id == bid_id)
        )
        result = await self.session.execute(stmt)
        bid_orm = result.scalar_one_or_none()

        if not bid_orm:
            return False
        
        bid_orm.deleted_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        return True
