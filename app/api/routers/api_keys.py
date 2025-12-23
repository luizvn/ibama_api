from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user, get_db
from app.db.session import AsyncSession
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyShow
from app.services import api_key_service

router = APIRouter(prefix="/api_keys", tags=["API Keys"])


@router.post("", response_model=ApiKeyCreated)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_active_user: User = Depends(get_current_active_user),
):
    api_key, raw_key = await api_key_service.create_api_key(
        db, current_active_user.id, data
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já atingiu o limite máximo de chaves de API (5 chaves).",
        )

    response = ApiKeyCreated.model_validate(api_key)
    response.key = raw_key

    return response


@router.patch("/{api_key_id}/disable", response_model=ApiKeyShow)
async def disable_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db),
    current_active_user: User = Depends(get_current_active_user),
):
    api_key = await api_key_service.disable_api_key(db, api_key_id, current_active_user)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found or access denied",
        )

    return api_key


@router.get("/{user_id}", response_model=list[ApiKeyShow])
async def get_api_keys_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_active_user: User = Depends(get_current_active_user),
):
    api_keys = await api_key_service.get_api_keys_by_user(
        db, user_id, current_active_user
    )

    if not api_keys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Keys não encontradas para o usuário.",
        )

    return api_keys
