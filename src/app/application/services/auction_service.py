from app.application.ports.auction_repository import AuctionRepository
from app.api.v1.schemas.auction import AuctionCreate, AuctionResponse
from app.domain.enums import AuctionState
from app.domain.models.auction import Auction
from app.domain.exceptions import AuctionNotFoundError
from typing import Optional
from uuid import UUID


class AuctionService:
    def __init__(self, auction_repo: AuctionRepository, logger):
        self.auction_repo = auction_repo
        self.logger = logger


    async def create_auction(self, auction_in: AuctionCreate, seller_id: UUID) -> AuctionResponse:
        """
        Crea una nueva subasta.
        """
        self.logger.info(f"Creando subasta para el usuario {seller_id}.")

        # Transformamos el esquema de entrada en un modelo de Dominio puro
        # Aquí es donde el Dominio genera su propio UUID.
        new_auction = Auction(
            title = auction_in.title,
            description = auction_in.description,
            starting_price = auction_in.starting_price,
            start_time = auction_in.start_time,
            end_time = auction_in.end_time,
            seller_id = seller_id,
            state = auction_in.state
        )

        try:
            return await self.auction_repo.create(new_auction)
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def list_auctions(self) -> list[Auction]:
        """
        Obtiene todas las subastas
        """
        self.logger.info(f"Se van a obtener todas las subastas")
        try:
            return await self.auction_repo.get_all()
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def get_auction(self, auction_id: UUID) -> Auction:
        """
       Obtiene una subasta por ID.
        """
        self.logger.info(f"Se va a obtener la subasta con ID {auction_id}")

        try:
            auction = await self.auction_repo.get_by_id(auction_id)
            if not auction:
                raise AuctionNotFoundError(f"La subasta con ID {auction_id} no existe.")
            return auction
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def update_details(
            self,
            auction_id: UUID,
            user_id: UUID,
            title: str,
            description: Optional[str] = None
    ) -> Auction:
        """
        Permite al vendedor corregir título o descripción.
        No permite cambiar precios ni fechas (por seguridad).
        """
        auction = await self.get_auction(auction_id)

        if auction.seller_id != user_id:
            raise PermissionError("Solo el vendedor puede editar esta subasta.")

        if auction.state == AuctionState.CANCELLED:
            raise ValueError("No se puede editar una subasta cancelada.")
        
        has_changed = auction.update_details(title, description)

        if has_changed:
            return await self.auction_repo.update(auction)
        
        return auction


    async def cancel_auction(self, auction_id: UUID, user_id: UUID) -> Auction:
        auction = await self.get_auction(auction_id)

        if auction.seller_id != user_id:
            raise PermissionError("No tienes permiso para cancelar esta subasta.")
        
        if auction.cancel():
            return await self.auction_repo.update(auction)
        
        return auction
