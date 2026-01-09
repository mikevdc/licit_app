from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional
from uuid import UUID


class BidBase(BaseModel):
    amount: Decimal


class BidCreate(BidBase):
    pass # Es igual a la base


class BidResponse(BidBase):
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None
    auction_id: UUID
    bidder_id: UUID

    # Configuración para leer desde ORM
    model_config = ConfigDict(from_attributes = True)
