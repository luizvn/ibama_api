from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, User
from app.api import deps
from app.services import user_service


router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    summary="Cria um novo usuário."
)
def create_user(
    user: UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    created_user = user_service.create_user(db, user)

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um usuário com este nome de usuário já existe."
        )

    return created_user