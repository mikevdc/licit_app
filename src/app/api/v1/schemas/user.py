from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length = 8)


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    # Configuración para leer desde ORM
    model_config = ConfigDict(from_attributes = True)
