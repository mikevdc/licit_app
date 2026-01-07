from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Annotated
from uuid import UUID


class AuctionCreate(BaseModel):
    title: Annotated[str, Field(min_length = 3, max_length = 100)]
    starting_price: Annotated[float, Field(gt = 0)]
    start_time: datetime
    end_time: datetime
    seller_id: UUID


    @model_validator(mode = 'after')
    def validate_dates(self) -> 'AuctionCreate':
        now = datetime.now(timezone.utc)

        # 1. ¿La subasta termina antes de empezar?
        if self.start_time >= self.end_time:
            raise ValueError("La fecha de finalización debe ser posterior al inicio.")
        
        # 2. ¿La subasta intenta empezar en el pasado?
        if self.start_time < now:
            raise ValueError("La subasta no puede empezar en el pasado.")
        
        return self
