from typing import AsyncGenerator
from app.db.session import AsyncSessionLocal, AsyncSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from app.models.user import User
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenData
from app.services import user_service
from app.models.user import UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(username=payload.get("sub"), role=payload.get("role"))

    except JWTError:
        raise credentials_exception

    if token_data.username is None:
        raise credentials_exception

    user = await user_service.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="O usuário está inativo."
        )

    return current_user


def get_current_active_admin_user(
    current_active_user: User = Depends(get_current_active_user),
) -> User:
    if current_active_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O usuário não tem permissão para acessar este recurso.",
        )

    return current_active_user

async def get_current_user_from_api_key(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(api_key_header),
) -> User | None:
    
    if not api_key:
        return None
    
    user = await user_service.get_user_by_api_key(db, api_key=api_key)
    
    return user

async def get_current_user_hybrid(
    api_key_user: User | None = Depends(get_current_user_from_api_key),
    token_user: User | None = Depends(get_current_user),
) -> User | None:
    
    user = api_key_user or token_user
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais de acesso.",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="O usuário está inativo."
        )
    
    return user