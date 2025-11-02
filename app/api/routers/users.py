from fastapi import APIRouter, Response, status, Depends, HTTPException
from app.schemas.user import PasswordUpdate, RoleUpdate, StatusUpdate, UserCreate, User
from app.api import deps
from app.services import user_service
from app.db.session import AsyncSession


router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    summary="Cria um novo usuário."
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    created_user = await user_service.create_user(db, user)

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um usuário com este nome de usuário já existe."
        )

    return created_user

@router.patch(
    "/{user_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Atualiza o status de um usuário."
)
async def update_user_status(
    user_id: int,
    user_status: StatusUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user)
):  
    if current_active_admin == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível alterar o status do próprio usuário."
        )

    updated_user = await user_service.update_user_status(db, user_id, user_status)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return updated_user

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[User],
    summary="Lista todos os usuários."
)
async def get_all_users(
    db: AsyncSession = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user)
):
    users = await user_service.get_all_users(db)

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
async def update_user_role(
    user_id: int,
    role: RoleUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_active_admin: User = Depends(deps.get_current_active_admin_user),
):
    if current_active_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível alterar o papel do próprio usuário."
        )
    
    updated_user = await user_service.update_user_role(db, user_id, role)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return updated_user

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativa a conta do próprio usuário logado."
)
async def deactivate_current_user(
    db: AsyncSession = Depends(deps.get_db),
    current_active_user: User = Depends(deps.get_current_active_user)
):
    await user_service.update_user_status(db, current_active_user.id, StatusUpdate(is_active=False))

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualiza a senha do próprio usuário logado."
)
async def update_current_user_password(
    password_update: PasswordUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_active_user: User = Depends(deps.get_current_active_user)
):
    is_changed = await user_service.update_current_user_password(
        db, 
        current_active_user.id, 
        password_update
    )

    if not is_changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)