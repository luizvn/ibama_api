from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: ClassVar[str] = "API de Autos de Infração - IBAMA"

    DATABASE_URL: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str

settings = Settings() # type: ignore