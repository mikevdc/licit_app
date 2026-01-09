from app.domain.enums import AuctionState
from app.infrastructure.db.base import Base
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

# Esto SOLO lo lee VS Code para ayudar con el autocompletado o, en este caso, 
# para que no marque un warning en "BidORM".
# Python lo ignora completamente al ejecutar la app
if TYPE_CHECKING:
    from app.infrastructure.db.models.bid_orm import BidORM
    from app.infrastructure.db.models.user_orm import UserORM


class AuctionORM(Base):
    __tablename__ = "auctions"

    # No hace falta especificar el tipo GUID aqui, lo hereda del type_annotation_map
    id: Mapped[UUID] = mapped_column(primary_key = True, default = uuid4)

    title: Mapped[str] = mapped_column(String(100), nullable = False)
    description: Mapped[str] = mapped_column(Text)

    # Numeric(12, 2) permite hasta 9.999.999.999'99 sin errores de redondeo
    starting_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable = False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable = False)

    # La DB debe ser UTC
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)

    state: Mapped[AuctionState] = mapped_column(Enum(AuctionState), default = AuctionState.ACTIVE, nullable = False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc), onupdate = lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone = True), nullable = True)

    # CLAVE FORÁNEA
    seller_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable = False)
    winner_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable = True)

    # RELACIONES
    # La relación inversa para acceder al objeto UserORM directamente
    seller: Mapped["UserORM"] = relationship(
        "UserORM", 
        back_populates = "auctions_created",
        foreign_keys = [seller_id]
    )

    winner: Mapped[Optional["UserORM"]] = relationship(
        "UserORM",
        back_populates = "auctions_won",
        foreign_keys = [winner_id]
    )

    # Una subasta tiene muchas pujas
    bids: Mapped[List["BidORM"]] = relationship("BidORM", back_populates = "auction")
