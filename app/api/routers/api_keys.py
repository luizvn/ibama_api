from fastapi import APIRouter
from app.schemas.api_key import ApiKeyCreated, ApiKeyCreate
from app.db.session import AsyncSession
from fastapi import Depends
from app.api.deps import get_current_active_user, get_db
from app.services import api_key_service
from app.models.user import User

router = APIRouter(prefix="/api_keys", tags=["API Keys"])

@router.post("", response_model=ApiKeyCreated)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_active_user: User = Depends(get_current_active_user),
):

    api_key, raw_key = await api_key_service.create_api_key(db, current_active_user.id, data)
    
    response = ApiKeyCreated.model_validate(api_key)
    response.key = raw_key
    
    return response
