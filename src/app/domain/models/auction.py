from app.domain.enums import AuctionState
from app.domain.exceptions import DomainError
from app.domain.models.bid import Bid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Auction:
    title: str
    description: Optional[str]
    starting_price: Decimal
    end_time: datetime
    seller_id: UUID
    state: AuctionState = AuctionState.ACTIVE
    current_price: Optional[Decimal] = None
    winner_id: Optional[UUID] = None

    id: UUID = field(default_factory = uuid4)
    start_time: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    
    bids: list[Bid] = field(default_factory = list)

    # Auditoría
    created_at: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Se ejecuta automáticamente justo después de crear la instancia.
        Aquí van las reglas de inicialización de negocio.
        """
        # Regla: Si no hay precio actual definido, el precio es el de salida
        if not self.current_price:
            self.current_price = self.starting_price

    @property
    def is_open(self) -> bool:
        """Combina el estado con el tiempo, para decidir si se puede pujar."""
        # 1. Debe estar activa
        if self.state != AuctionState.ACTIVE:
            return False
         
        # 2. Debe estar dentro del rango de tiempo
        if not(self.start_time <= datetime.now(timezone.utc) <= self.end_time):
            return False
        return True
    

    def update_details(self, title: str = None, description: str = None) -> bool:
        """
        Método centralizado para modificar el título y/o la descripción de la subasta.
        Garantiza que updated_at SIEMPRE se refresque.
        """
        changed = False
        if title and title != self.title:
            self.title = title
            changed = True
        if description and description != self.description:
            self.description = description
            changed = True
        
        if changed:
            self.updated_at = datetime.now(timezone.utc)

        return changed

    
    def cancel(self) -> bool:
        """Devuelve True si se canceló, False si ya estaba cancelada"""
        if self.state == AuctionState.CANCELLED:
            return False
        
        if self.state == AuctionState.COMPLETED:
            raise ValueError("No se puede cancelar una subasta finalizada")
        
        self.state = AuctionState.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
        return True


    def place_bid(self, amount: Decimal, bidder_id: UUID) -> None:
        """ 
        Método para añadir pujas.
        """
        # 1. Validar tiempo y estado
        if not self.is_open:
            if datetime.now(timezone.utc) > self.end_time:
                raise ValueError("La subasta ha finalizado.")
            raise ValueError("La subasta no está activa.")
        
        # 2. Validar que no puje el propio vendedor
        if bidder_id == self.seller_id:
            raise ValueError("El vendedor no puede pujar en su propia subasta.")
        
        # 3. Validar precio
        if amount <= self.current_price:
            raise ValueError(f"La puja ({amount}) debe superar el precio actual de {self.current_price}")
        
        # 4. Crear la entidad Puja
        new_bid = Bid(
            amount = amount,
            bidder_id = bidder_id,
            auction_id = self.id
        )

        # 5. Actualizar el estado de la subasta
        self.bids.append(new_bid)
        self.current_price = amount
        self.winner_id = bidder_id
        self.updated_at = datetime.now(timezone.utc)

        return new_bid
