from app.infrastructure.db.models.types import GUID
from sqlalchemy.orm import DeclarativeBase
from uuid import UUID


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos ORM del sistema.

    Al heredar de DeclarativeBase, esta clase mantiene un registro (metadata)
    de todas las tablas definidas en el sistema.
    """
    # Esto mapea automáticamente el tipo de Python UUID al tipo GUID de SQLAlchemy
    type_annotation_map = {
        UUID: GUID,
    }
