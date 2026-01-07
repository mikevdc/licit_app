from app.infrastructure.db.base import Base
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.mysql import CHAR # Para el UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

# Esto SOLO lo lee VS Code para ayudar con el autocompletado o, en este caso, 
# para que no marque un warning en "AuctionORM".
# Python lo ignora completamente al ejecutar la app
if TYPE_CHECKING:
    from app.infrastructure.db.models.auction_orm import AuctionORM
    from app.infrastructure.db.models.user_orm import UserORM

class BidORM(Base):
    __tablename__ = "bids"

    # No hace falta especificar el tipo GUID aqui, lo hereda del type_annotation_map
    id: Mapped[UUID] = mapped_column(primary_key = True, default = uuid4)

    # Numeric(12, 2) permite hasta 9.999.999.999'99 sin errores de redondeo
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable = False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))

    # RELACIONES
    # Una puja pertenece a una subasta
    auction_id: Mapped[UUID] = mapped_column(CHAR(36), ForeignKey("auctions.id"), nullable = False)

    # La relación inversa para acceder al objeto AuctionORM directamente
    auction: Mapped["AuctionORM"] = relationship("AuctionORM", back_populates = "bids")

    # Una puja pertenece a un usuario
    bidder_id: Mapped[UUID] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable = False)
    
    # La relación inversa para acceder al objeto UserORM directamente
    bidder: Mapped["UserORM"] = relationship("UserORM", back_populates = "bids")
