from datetime import datetime, timezone
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Bid(BaseModel):
    id: UUID = Field(default_factory = uuid4)
    amount: float = Field(gt = 0)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    bidder_id: UUID
    auction_id: UUID


    def is_bid_bigger(self, value):
        """
        Comprueba si esta puja es mayor que un valor dado
        """
        return self.amount > value
