from app.domain.exceptions import AuctionCreationError
from app.domain.models.auction import Auction, Bid
from app.infrastructure.db.models.auction_orm import AuctionORM
from app.infrastructure.db.models.bid_orm import BidORM
from app.application.ports.auction_repository import AuctionRepository
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class SQLAlchemyAuctionRepository(AuctionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    

    # --- MAPPERS ---
    def _to_orm(self, auction: Auction) -> AuctionORM:
        """Dominio (@dataclass) -> BD (ORM)"""
        return AuctionORM(
            id = auction.id,
            title = auction.title,
            description = auction.description,
            starting_price = auction.starting_price,
            current_price = auction.current_price,
            start_time = auction.start_time,
            end_time = auction.end_time,
            state = auction.state,
            seller_id = auction.seller_id,
            created_at = auction.created_at,
            updated_at = auction.updated_at,
            deleted_at = auction.deleted_at
        )
    

    def _to_domain(self, auction_orm: AuctionORM) -> Auction:
        """BD (ORM) -> Dominio (@dataclass)"""
        # Mapeamos las pujas si SQLAlchemy las cargó (lazy vs eager)
        domain_bids = []
        if 'bids' in auction_orm.__dict__:
            domain_bids = [self._bid_to_domain(b) for b in auction_orm.bids]

        return Auction(
            id = auction_orm.id,
            title = auction_orm.title,
            description = auction_orm.description,
            starting_price = auction_orm.starting_price,
            current_price = auction_orm.current_price,
            start_time = auction_orm.start_time,
            end_time = auction_orm.end_time,
            state = auction_orm.state,
            seller_id = auction_orm.seller_id,
            winner_id = auction_orm.winner_id,
            bids = domain_bids,
            created_at = auction_orm.created_at,
            updated_at = auction_orm.updated_at,
            deleted_at = auction_orm.deleted_at
        )


    def _bid_to_domain(self, bid_orm: BidORM) -> Bid:
        """Helper para convertir una Puja ORM a Dominio."""
        return Bid(
            id = bid_orm.id,
            amount = bid_orm.amount,
            bidder_id = bid_orm.bidder_id,
            auction_id = bid_orm.auction_id,
            created_at = bid_orm.created_at
        )
    
    def _update_orm_from_domain(self, auction_orm: AuctionORM, auction: Auction) -> None:
        """
        Transfiere los datos del Dominio al objeto ORM **ya existente** y **atacheado**.
        Esto permite que SQLAlchemy detecte solo los campos que han cambiado (Dirty Checking).
        """
        auction_orm.current_price = auction.current_price
        auction_orm.winner_id = auction.winner_id
        auction_orm.state = auction.state
        auction_orm.updated_at = auction.updated_at
        auction_orm.deleted_at = auction.deleted_at
        # La lista 'bids' no la actualizamos aquí directamente para evitar complejidad excesiva con SQLAlchemy.
        # Las pujas se insertan como entidades separadas a través de BidRepository

    
    # --- IMPLEMENTACIÓN DE LA INTERFAZ ---
    async def create(self, auction: Auction) -> Auction:
        auction_orm = self._to_orm(auction)
        try:
            self.session.add(auction_orm)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise AuctionCreationError(f"No se pudo crear la subasta. Verifica que el vendedor {auction.seller_id} exista.")
        
        return auction
    

    async def get_all(self) -> list[Auction]:
        stmt = (
            select(AuctionORM)
        )
        result = await self.session.execute(stmt)
        auction_orm = result.scalars().all()
        return [self._to_domain(auction) for auction in auction_orm]


    async def get_by_id(self, auction_id: UUID) -> Auction | None:
        # Usamos selectinload para traer las pujas eficientemente en la misma query (o query secundaria optimizada)
        stmt = (
            select(AuctionORM)
            .where(AuctionORM.id == auction_id)
            .options(selectinload(AuctionORM.bids))
        )
        result = await self.session.execute(stmt)
        auction_orm = result.scalar_one_or_none()
        return self._to_domain(auction_orm) if auction_orm else None


    async def update(self, auction: Auction) -> Auction:
        stmt = (
            select(AuctionORM)
            .where(AuctionORM.id == auction.id)
        )
        result = await self.session.execute(stmt)
        auction_orm = result.scalar_one_or_none()

        if not auction_orm:
            raise ValueError(f"Subasta {auction.id} no encontrada para actualizar.")

        self._update_orm_from_domain(auction_orm, auction)

        await self.session.commit()
        return auction
