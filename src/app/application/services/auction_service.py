from app.application.ports.auction_repository import AuctionRepository
from app.api.v1.schemas.auction import AuctionCreate, AuctionResponse
from app.domain.models import Auction
from app.domain.exceptions import AuctionNotFoundError
from uuid import UUID


class AuctionService:
    def __init__(self, repository: AuctionRepository, logger):
        self.repository = repository
        self.logger = logger


    async def create_auction(self, auction_in: AuctionCreate, seller_id: UUID) -> AuctionResponse:
        """
        Caso de Uso: Crear una nueva subasta.
        """
        self.logger.info(f"Creando subasta para el usuario {seller_id}.")

        # Transformamos el esquema de entrada en un modelo de Dominio puro
        # Aquí es donde el Dominio genera su propio UUID.
        new_auction = Auction(
            title = auction_in.title,
            starting_price = auction_in.starting_price,
            start_time = auction_in.start_time,
            end_time = auction_in.end_time,
            seller_id = seller_id
        )

        try:
            return await self.repository.save(new_auction)
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e


    async def get_auction(self, auction_id: UUID) -> Auction:
        """
        Caso de Uso: Obtener una subasta por ID.
        """
        self.logger.info(f"Se va a obtener la subasta con ID {auction_id}")

        try:
            auction = await self.repository.get_by_id(auction_id)
            if not auction:
                raise AuctionNotFoundError(f"La subasta con ID {auction_id} no existe.")
            return auction
        
        except Exception as e:
            self.logger.error(f"{e}", exc_info = True)
            raise e
