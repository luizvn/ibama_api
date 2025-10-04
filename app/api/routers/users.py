from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import RoleUpdate, UserCreate, User
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
    db: Session = Depends(deps.get_db)
):
    created_user = user_service.create_user(db, user)

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um usuário com este nome de usuário já existe."
        )

    return created_user

@router.patch(
    "/{user_id}/deactivate",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Desativa um usuário."
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user)
):  
    if current_active_admin == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível desativar o próprio usuário."
        )

    deactivated_user = user_service.deactivate_user(db, user_id)

    if not deactivated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return deactivated_user

@router.patch(
    "/{user_id}/activate",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Reativa um usuário."
)
def activate_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user)
):  
    if current_active_admin == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível reativar o próprio usuário."
        )

    activated_user = user_service.activate_user(db, user_id)

    if not activated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return activated_user

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[User],
    summary="Lista todos os usuários."
)
def get_all_users(
    db: Session = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user)
):
    users = user_service.get_all_users(db)

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuário encontrado."
        )

    return users

@router.patch(
    "/{user_id}/role",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Atualiza o papel de um usuário."
)
def update_user_role(
    user_id: int,
    role: RoleUpdate,
    db: Session = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user),
):
    if current_active_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível alterar o papel do próprio usuário."
        )
    
    updated_user = user_service.update_user_role(db, user_id, role)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return updated_user
