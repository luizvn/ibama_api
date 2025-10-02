from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.core.security import verify_password
from sqlalchemy import select
from app.models.user import User 
from app.core.security import get_password_hash


def get_user_by_username(
    db: Session, 
    username: str
) -> User | None:
    statement = select(User).where(User.username == username)
    user = db.execute(statement).scalar_one_or_none()
    return user

def authenticate_user(
    db: Session, 
    username: str, 
    password: str
) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 

def create_user(
    db: Session, 
    user: UserCreate
) -> User | None:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        return None

    new_user = User(
        username=user.username, 
        hashed_password=get_password_hash(user.password), 
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def deactivate_user(
    db: Session, 
    user_id: int
) -> User | None:
    user_to_deactivate = db.get(User, user_id)
    if not user_to_deactivate:
        return None
    
    user_to_deactivate.is_active = False
    db.commit()
    db.refresh(user_to_deactivate)

    return user_to_deactivate

def activate_user(
    db: Session, 
    user_id: int
) -> User | None:
    user_to_activate = db.get(User, user_id)
    if not user_to_activate:
        return None

    user_to_activate.is_active = True
    db.commit()
    db.refresh(user_to_activate)

    return user_to_activate

def get_all_users(
    db: Session
) -> list[User] | None:
    
    stmt = select(User)
    users = list(db.scalars(stmt).all())

    if not users:
        return None

    return users
