import os
from pydantic_settings import BaseSettings
from typing import ClassVar

class Settings(BaseSettings):

    PROJECT_NAME: ClassVar[str] = "API de Autos de Infração - IBAMA"

    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()