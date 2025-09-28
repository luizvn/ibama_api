from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password
from sqlalchemy import select


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = db.execute(statement).scalar_one_or_none()
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 