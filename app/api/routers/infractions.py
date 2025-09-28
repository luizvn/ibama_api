from fastapi import APIRouter, status, BackgroundTasks, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.ingestion_service import IngestionService
from app.models.user import User  # noqa: F401
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infractions", tags=["Infractions"])

@router.post(
    "/upload-csv",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Envia um arquivo CSV para ingestão assíncrona de infrações.",
)
def upload_infractions_csv(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    file: UploadFile = File(..., description="Arquivo CSV contendo os dados das infrações.")
):  
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido ou sem nome. Apenas arquivos .csv são aceitos."
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
    finally:
        file.file.close()

    logger.info(
        f"Usuário '{current_user.username}' (ID: {current_user.id}) "
        f"enviou o arquivo '{file.filename}' para processamento."
    )
    
    service = IngestionService(db)
    background_tasks.add_task(service.process_csv, temp_file_path)

    return{
        "message": "Arquivo recebido. O processamento será feito em segundo plano.",
        "filename": file.filename
    }