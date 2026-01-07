import uuid

from sqlalchemy.types import TypeDecorator, CHAR

class GUID(TypeDecorator):
    """
    Tipo de dato para manejar UUIDs de forma transparente en MariaDB.
    Python (UUID) <-> MariaDB (CHAR(36) string)
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return value # Por si ya viene como string
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value
