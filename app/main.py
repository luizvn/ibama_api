from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.routers import auth, infractions
from app.core.logging_config import setup_logging


setup_logging()

app = FastAPI(
    title="API de Autos de Infração - IBAMA",
    description="API para consulta de autos de infração do IBAMA.",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(infractions.router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    """
    Verifica a saúde da aplicação e a conexão com o banco de dados.
    """
    try:
        # Tenta executar uma consulta simples para verificar a conexão com o BD
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # Se a conexão falhar, o endpoint levantará uma exceção
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "error", 
                "database": "disconnected",
                "error_details": str(e)
            }
        )