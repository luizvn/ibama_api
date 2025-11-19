from fastapi import APIRouter, Depends, HTTPException, status
from app.services import user_service
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.token import Token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.config import settings
from app.core import security
import asyncio


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await user_service.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await asyncio.to_thread(
        security.create_access_token,
        subject=user.username,
        role=user.role,
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
