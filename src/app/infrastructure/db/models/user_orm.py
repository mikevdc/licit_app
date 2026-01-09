from app.infrastructure.db.base import Base
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

# Esto SOLO lo lee VS Code para ayudar con el autocompletado o, en este caso, 
# para que no marque un warning en "BidORM".
# Python lo ignora completamente al ejecutar la app
if TYPE_CHECKING:
    from app.infrastructure.db.models.auction_orm import AuctionORM
    from app.infrastructure.db.models.bid_orm import BidORM

class UserORM(Base):
    __tablename__ = "users"

    # No hace falta especificar el tipo GUID aqui, lo hereda del type_annotation_map
    id: Mapped[UUID] = mapped_column(primary_key = True, default = uuid4)

    username: Mapped[str] = mapped_column(String(50), unique = True, index = True, nullable = False)
    email: Mapped[str] = mapped_column(String(255), unique = True, index = True, nullable = False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable = False)

    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default = False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc), onupdate = lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone = True), nullable = True)

    # RELACIONES
    # 1. Subastas que realiza este usuario
    auctions_created: Mapped[List["AuctionORM"]] = relationship(
        "AuctionORM",
        back_populates = "seller", # Debo asegurarme de que en AuctionORM el campo se llame 'seller'
        foreign_keys = "[AuctionORM.seller_id]" # Especifico qué FK usar
    )

    # 2. Subastas que ha ganado este usuario
    auctions_won: Mapped[List["AuctionORM"]] = relationship(
        "AuctionORM",
        back_populates = "winner", # Debo asegurarme de que en AuctionORM el campo se llame 'winner'
        foreign_keys = "[AuctionORM.winner_id]"
    )

    # Un usuario puede realizar muchas pujas
    bids: Mapped[List["BidORM"]] = relationship(
        "BidORM",
        back_populates = "bidder" # Debo asegurarme de que en BidORM el campo se llame 'bidder'
    )
