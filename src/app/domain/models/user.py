from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4


class User(BaseModel):
    id: UUID = Field(default_factory = uuid4)
    username: str = Field(..., min_length = 3, max_length = 50, description = "Nombre único del usuario")
    email: EmailStr = Field(..., description = "Correo electrónico válido")
    password_hash: str = Field(...)
    is_active: bool = Field(default = True)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))


    def activate(self):
        """
        Activa el usuario
        """
        self.is_active = True

    
    def deactivate(self):
        """
        Desactiva el usuario
        """
        self.is_active = False
    

    def __str__(self):
        return self.username
