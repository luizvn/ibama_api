from sqlalchemy.orm import Session
from app.schemas.user import PasswordUpdate, RoleUpdate, StatusUpdate, UserCreate
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
    if not user.is_active:
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

def update_user_status(
    db: Session, 
    user_id: int,
    user_status: StatusUpdate
) -> User | None:
    user_to_update = db.get(User, user_id)

    if not user_to_update:
        return None

    user_to_update.is_active = user_status.is_active

    db.commit()
    db.refresh(user_to_update)

    return user_to_update

def get_all_users(
    db: Session
) -> list[User] | None:
    
    stmt = select(User)
    users = list(db.scalars(stmt).all())

    if not users:
        return None

    return users

def update_user_role(
    db: Session, 
    user_id: int,
    role: RoleUpdate
) -> User | None:
    user_to_update = db.get(User, user_id)
    
    if not user_to_update:
        return None
    
    user_to_update.role = role.role

    db.commit()
    db.refresh(user_to_update)

    return user_to_update

def update_current_user_password(
    db: Session, 
    user_id: int, 
    password_update: PasswordUpdate
) -> bool:
    user_to_update = db.get(User, user_id)

    if not user_to_update:
        return False

    if not verify_password(password_update.old_password, user_to_update.hashed_password):
        return False

    user_to_update.hashed_password = get_password_hash(password_update.new_password)

    db.commit()
    db.refresh(user_to_update)

    return True