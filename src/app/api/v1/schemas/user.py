from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 50)
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length = 8)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Configuración para leer desde ORM
    model_config = ConfigDict(from_attributes = True)
