from app.schemas.user import PasswordUpdate, RoleUpdate, StatusUpdate, UserCreate
from app.core.security import verify_password
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash
from app.db.session import AsyncSession
import asyncio


async def get_user_by_username(
    db: AsyncSession, 
    username: str
) -> User | None:
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    return user

async def authenticate_user(
    db: AsyncSession, 
    username: str, 
    password: str
) -> User | None:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not user.is_active:
        return None
    is_valid_password = await asyncio.to_thread(
        verify_password, 
        password, 
        user.hashed_password
    )
    if not is_valid_password:
        return None
    return user 

async def create_user(
    db: AsyncSession, 
    user: UserCreate
) -> User | None:
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        return None

    hashed_password = await asyncio.to_thread(
        get_password_hash, 
        user.password
    )

    new_user = User(
        username=user.username, 
        hashed_password=hashed_password, 
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def update_user_status(
    db: AsyncSession, 
    user_id: int,
    user_status: StatusUpdate
) -> User | None:
    user_to_update = await db.get(User, user_id)

    if not user_to_update:
        return None

    user_to_update.is_active = user_status.is_active

    await db.commit()
    await db.refresh(user_to_update)

    return user_to_update

async def get_all_users(
    db: AsyncSession
) -> list[User] | None:
    
    stmt = select(User)
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    if not users:
        return None

    return users

async def update_user_role(
    db: AsyncSession, 
    user_id: int,
    role: RoleUpdate
) -> User | None:
    user_to_update = await db.get(User, user_id)
    
    if not user_to_update:
        return None
    
    user_to_update.role = role.role

    await db.commit()
    await db.refresh(user_to_update)

    return user_to_update

async def update_current_user_password(
    db: AsyncSession, 
    user_id: int, 
    password_update: PasswordUpdate
) -> bool:
    user_to_update = await db.get(User, user_id)

    if not user_to_update:
        return False
    is_valid_password = await asyncio.to_thread(
        verify_password, 
        password_update.old_password, 
        user_to_update.hashed_password
    )
    if not is_valid_password:
        return False
    
    new_hashed_password = await asyncio.to_thread(
        get_password_hash, 
        password_update.new_password
    )

    user_to_update.hashed_password = new_hashed_password

    await db.commit()
    await db.refresh(user_to_update)

    return True