from app.domain.exceptions import DomainError
from app.domain.models.bid import Bid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4


class Auction(BaseModel):
    id: UUID = Field(default_factory = uuid4)
    title: str = Field(..., min_length = 5, max_length = 255)
    starting_price: float = Field(..., gt = 0)    
    start_time: datetime
    end_time: datetime
    deleted_at: Optional[datetime] = Field(default = None)
    seller_id: UUID
    bids: list[Bid] = Field(default_factory = list)

    @property
    def current_price(self) -> float:
        """
        Calcula el precio actual basado en las pujas existentes.
        -> Si no hay pujas, es el precio de salida.
        -> Si hay, es la puja más alta.
        """
        return max([bid.amount for bid in self.bids], default = self.starting_price)
    

    def add_bid(self, user_id: UUID, amount: float, current_time: datetime):
        """Encapsula la lógica de negocio. El objeto se protege a sí mismo."""
        if not(self.start_time <= current_time <= self.end_time):
            raise DomainError("La subasta ya no está activa.")

        if amount <= self.current_price:
            raise DomainError(f"La puja debe ser mayor a {self.current_price}")

        new_bid = Bid(user_id = user_id, amount = amount, timestamp = current_time)
        self.bids.append(new_bid)        
