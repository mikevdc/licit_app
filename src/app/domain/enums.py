from enum import StrEnum, auto

class AuctionState(StrEnum):
    """auto() hace que el valor asignado sea automáticamente el nombre del miembro en minúsculas."""
    DRAFT = auto() # "draft"
    ACTIVE = auto() # "active"
    COMPLETED = auto() # "completed"
    CANCELLED = auto() # "cancelled"
