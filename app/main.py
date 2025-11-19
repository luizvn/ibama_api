from fastapi import FastAPI
from app.api.routers import auth, infractions, users
from app.core.logging_config import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


setup_logging()

app = FastAPI(
    title="API de Autos de Infração - IBAMA",
    description="API para consulta de autos de infração do IBAMA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(infractions.router)
app.include_router(users.router)
