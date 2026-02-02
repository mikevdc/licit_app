from app.domain.enums import AuctionState
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Annotated, Optional, Self
from uuid import UUID


class AuctionBase(BaseModel):
    title: Annotated[str, Field(min_length = 3, max_length = 100)]
    description: Optional[str] = None
    starting_price: Annotated[Decimal, Field(gt = 0)]
    start_time: Optional[datetime] = None # Si es None, empieza ya
    end_time: datetime
    state: AuctionState = AuctionState.ACTIVE


class AuctionCreate(AuctionBase):

    @model_validator(mode = 'after')
    def validate_dates(self) -> 'Self':
        now = datetime.now(timezone.utc)

        if self.end_time.tzinfo is None:
            self.end_time = self.end_time.replace(tzinfo = timezone.utc)

        if self.start_time:
            if self.start_time.tzinfo is None:
                self.start_time = self.start_time.replace(tzinfo = timezone.utc)

            # 1. ¿La subasta termina antes de empezar?
            if self.start_time >= self.end_time:
                raise ValueError("La fecha de finalización debe ser posterior al inicio.")

            # 2. ¿La subasta intenta empezar en el pasado?
            if self.start_time < now:
                raise ValueError("La subasta no puede empezar en el pasado.")
        
        return self


class AuctionResponse(AuctionBase):
    id: UUID
    current_price: Decimal
    seller_id: UUID
    winner_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Configuración para leer desde ORM
    model_config = ConfigDict(from_attributes = True)
