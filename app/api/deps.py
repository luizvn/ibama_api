from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal 
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenData
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username) # noqa: F841
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="O usuário está inativo."
        )
    
    return current_user