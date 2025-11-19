from pydantic import BaseModel, ConfigDict, Field
from app.models.user import UserRole
import re


USERNAME_REGEX = re.compile(r"^[a-z0-9_]{4,15}$")

PASSWORD_REGEX = re.compile(r"^[A-Za-z0-9!@#$%&*()_+\-=]{8,15}$")


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=4,
        max_length=15,
        pattern=USERNAME_REGEX,
        description="O nome de usuário deve ter entre 4 e 15 caracteres e pode conter letras minúsculas, números e underlines(_).",
    )


class RoleUpdate(BaseModel):
    role: UserRole


class StatusUpdate(BaseModel):
    is_active: bool


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=15,
        pattern=PASSWORD_REGEX,
        description="A nova senha deve ter entre 8 e 15 caracteres e pode conter letras, números e caracteres especiais.",
    )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=15,
        pattern=PASSWORD_REGEX,
        description="A senha deve ter entre 8 e 15 caracteres.",
    )


class User(UserBase):
    id: int
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
