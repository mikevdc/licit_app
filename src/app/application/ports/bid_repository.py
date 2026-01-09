from abc import ABC, abstractmethod
from app.domain.models.bid import Bid
from uuid import UUID


class BidRepository(ABC):
    """
    Puerto de salida: Interfaz abstracta para la persistencia de subastas.
    No sabe nada de SQLAlchemy, solo conoce modelos de dominio.
    """


    @abstractmethod
    async def create(self, bid: Bid) -> Bid:
        """Persiste una nueva puja en el sistema."""
        raise NotImplementedError
    

    @abstractmethod
    async def get_by_id(self, bid_id: UUID) -> Bid | None:
        """Recupera una puja por su ID único."""
        raise NotImplementedError
    
    
    @abstractmethod
    async def get_by_auction_id(self, auction_id: UUID) -> list[Bid]:
        """Recupera todas las pujas de una subasta (Historial)."""
        pass


    @abstractmethod
    async def delete(self, bid_id: UUID) -> bool:
        """Ejecuta el borrado lógico de una puja. Devuelve True si la puja existía y fue borrada."""
        pass
