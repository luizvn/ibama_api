from fastapi import APIRouter, status, BackgroundTasks, Depends, UploadFile, File, HTTPException, Query
from app.api import deps
from app.services.ingestion_service import IngestionService
from app.models.user import User  # noqa: F401
import logging
import tempfile
import shutil
from app.schemas.infraction import InfractionPublic, Page
from datetime import date
from decimal import Decimal
from app.services import infraction_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infractions", tags=["Infractions"])

@router.post(
    "/upload-csv",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Envia um arquivo CSV para ingestão assíncrona de infrações.",
)
def upload_infractions_csv(
    background_tasks: BackgroundTasks,
    current_active_admin: User = Depends(deps.get_current_active_admin_user),
    file: UploadFile = File(..., description="Arquivo CSV contendo os dados das infrações.")
):  
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido ou sem nome. Apenas arquivos .csv são aceitos."
        )
    
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo inválido: {file.content_type}. Apenas arquivos CSV são aceitos."
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
    finally:
        file.file.close()

    logger.info(
        f"Usuário '{current_active_admin.username}' (ID: {current_active_admin.id}) "
        f"enviou o arquivo '{file.filename}' para processamento."
    )
    
    service = IngestionService()
    background_tasks.add_task(service.process_csv, temp_file_path)

    return{
        "message": "Arquivo recebido. O processamento será feito em segundo plano.",
        "filename": file.filename
    }


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[InfractionPublic],
    summary="Busca e lista infrações com filtros e paginação.",
)
def get_infractions(
    db = Depends(deps.get_db),
    current_active_user: User = Depends(deps.get_current_active_user),
    page: int = Query(1, ge=1, description="Número da página."),
    size: int = Query(50, ge=1, le=200, description="Quantidade de itens por página."),
    source_id: int | None = Query(None, description="Busca por ID da base de dados do IBAMA exata."),
    infraction_number: str | None = Query(None, description="Busca por número da infração exato."),
    offender_name: str | None = Query(None, description="Busca por parte do nome do infrator."),
    offender_document: str | None = Query(None, description="Busca por CPF/CNPJ exato do infrator."),
    start_date: date | None = Query(None, description="Data inicial da infração (YYYY-MM-DD)."),
    end_date: date | None = Query(None, description="Data final da infração (YYYY-MM-DD)."),
    min_fine_value: Decimal | None = Query(None, ge=0, description="Valor mínimo da multa."),
    municipality: str | None = Query(None, description="Busca por parte do nome do município."),
    state: str | None = Query(None, min_length=2, max_length=2, description="Busca por UF."),
    affected_biomes: str | None = Query(None, description="Busca por biomas afetados.")
):
    skip = (page - 1) * size
    
    total, infractions_data = infraction_service.get_infractions(
        db,
        skip=skip,
        limit=size,
        source_id=source_id,
        infraction_number=infraction_number,
        offender_name=offender_name,
        offender_document=offender_document,
        start_date=start_date,
        end_date=end_date,
        min_fine_value=min_fine_value,
        municipality=municipality,
        state=state,
        affected_biomes=affected_biomes
    )

    return {
        "total": total,
        "page": page,
        "size": len(infractions_data),
        "items": infractions_data
    }