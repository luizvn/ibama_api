from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)