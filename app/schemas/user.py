from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str

class RoleUpdate(BaseModel):
    role: UserRole

class StatusUpdate(BaseModel):
    is_active: bool

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)