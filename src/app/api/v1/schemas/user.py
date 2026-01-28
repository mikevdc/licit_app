from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

# Base común
class UserBase(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 50)
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


# -- INPUTS (Lo que se recibe de la API) ---
class UserCreate(UserBase):
    password: str = Field(..., min_length = 8)

class UserUpdate(BaseModel):
    # Todo opcional para permitir actualizaciones parciales
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str


# --- OUTPUTS (Lo que se devuelve al cliente) ---
class UserResponse(UserBase):
    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Configuración para leer desde ORM
    model_config = ConfigDict(from_attributes = True)
