from app.infrastructure.db.base import Base
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.mysql import CHAR # Para el UUID
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

    # Seguridad: Aquí guardaremos el hash, NUNCA la contraseña en plano
    password_hash: Mapped[str] = mapped_column(String(255), nullable = False)

    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone = True), nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))

    # RELACIONES
    # Un usuario puede crear muchas subastas
    auctions: Mapped[List["AuctionORM"]] = relationship(
        "AuctionORM",
        back_populates = "seller" # Debo asegurarme de que en AuctionORM el campo se llame 'seller'
    )

    # Un usuario puede realizar muchas pujas
    bids: Mapped[List["BidORM"]] = relationship(
        "BidORM",
        back_populates = "bidder" # Debo asegurarme de que en BidORM el campo se llame 'seller'
    )
