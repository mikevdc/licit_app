from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class User:
    username: str
    email: str
    password_hash: str
    is_active: bool = True
    is_superuser: bool = False
    id: UUID = field(default_factory = uuid4)

    # Auditoría
    created_at: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory = lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None


    def delete(self):
        """
        Lógica de borrado lógico (Soft Delete).
        Un usuario borrado de desactiva y se marca la fecha.
        """
        self.is_active = False
        now = datetime.now(timezone.utc)
        self.deleted_at = now
        self.updated_at = now

    
    def reactivate(self):
        """Reactiva un usuario borrado."""
        self.is_active = True
        self.deleted_at = None
        self.updated_at = datetime.now(timezone.utc)

    
    def update_details(self, email: str = None, username: str = None, is_active: bool = None) -> bool:
        """
        Método centralizado para modificar datos del usuario.
        Garantiza que updated_at SIEMPRE se refresque.
        """
        changed = False
        if email and email != self.email:
            self.email = email
            changed = True
        if username and username != self.username:
            self.username = username
            changed = True
        if is_active is not None and is_active != self.is_active:
            self.is_active = is_active
            changed = True
        
        if changed:
            self.updated_at = datetime.now(timezone.utc)

        return changed
    

    def __str__(self):
        return self.username
