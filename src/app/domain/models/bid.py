from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Bid:
    amount: Decimal
    auction_id: UUID
    bidder_id: UUID
    id: UUID = field(default_factory = uuid4)

    # Auditoría
    created_at: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None


    def delete(self):
        """Realiza un Soft Delete sobre la puja"""
        self.deleted_at = datetime.now(timezone.utc)
