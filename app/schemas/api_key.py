from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Nome identificador da chave")
    days_to_expire: int | None = Field(None, description="Quantidade de dias para expirar a chave (opcional)")

class ApiKeyShow(BaseModel):
    id: int = Field(..., description="ID da chave")
    name: str = Field(..., description="Nome identificador da chave")
    prefix: str = Field(..., description="Prefixo da chave")
    is_active: bool = Field(..., description="Indica se a chave está ativa")
    created_at: datetime = Field(..., description="Data de criação da chave")
    expires_at: datetime | None = Field(None, description="Data de expiração da chave")

    class Config:
        from_attributes = True

class ApiKeyCreated(ApiKeyShow):
    key: str = Field(..., description="A chave API completa. Exiba isso apenas uma vez!")
