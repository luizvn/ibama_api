from passlib.context import CryptContext
from typing import Any, Union
from datetime import timedelta, datetime, timezone
from app.core.config import settings
from jose import jwt

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(unhashed_password: str, hashed_password: str) -> bool:
    return password_context.verify(unhashed_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt