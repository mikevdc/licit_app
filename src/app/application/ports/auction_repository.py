from abc import ABC, abstractmethod
from app.domain.models.auction import Auction
from uuid import UUID


class AuctionRepository(ABC):
    """
    Puerto de salida: Interfaz abstracta para la persistencia de subastas.
    No sabe nada de SQLAlchemy, solo conoce modelos de dominio.
    """


    @abstractmethod
    async def create(self, auction: Auction) -> Auction:
        """Persiste una nueva subasta en el sistema."""
        raise NotImplementedError
    

    @abstractmethod
    async def get_by_id(self, auction_id: UUID) -> Auction | None:
        """Recupera una subasta por su ID único."""
        raise NotImplementedError
    
    
    @abstractmethod
    async def update(self, auction: Auction) -> Auction:
        "Actualiza el estado de una subasta existente."
        raise NotImplementedError
