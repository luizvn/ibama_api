from fastapi import FastAPI

app = FastAPI(
    title="API de Autos de Infração - IBAMA",
    description="API para consulta de autos de infração do IBAMA.",
    version="0.1.0"
)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}