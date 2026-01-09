from app.infrastructure.db.base import Base
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
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
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable = False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone = True), nullable = True)

    # CLAVE FORÁNEA
    auction_id: Mapped[UUID] = mapped_column(ForeignKey("auctions.id"), nullable = False)
    bidder_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable = False)

    # RELACIONES
    # La relación inversa para acceder al objeto AuctionORM directamente
    auction: Mapped["AuctionORM"] = relationship("AuctionORM", back_populates = "bids")
    
    # La relación inversa para acceder al objeto UserORM directamente
    bidder: Mapped["UserORM"] = relationship("UserORM", back_populates = "bids")
