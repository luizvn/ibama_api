import secrets
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.security import get_password_hash, verify_password
from app.models.api_key import ApiKey
from app.models.user import User, UserRole
from app.schemas.api_key import ApiKeyCreate
from app.core.redis import redis_client
import json

KEY_PREFIX = "ibama_"
CACHE_TTL = 600

async def create_api_key(
    db: AsyncSession,
    user_id: int,
    data: ApiKeyCreate
) -> tuple[ApiKey, str]:
    
    raw_secret = secrets.token_urlsafe(32)

    prefix_part = secrets.token_hex(4)

    final_key = f"{KEY_PREFIX}{prefix_part}.{raw_secret}"

    db_prefix = f"{KEY_PREFIX}{prefix_part}"

    hashed_key = get_password_hash(final_key)

    expires_at = None

    if data.days_to_expire:
        expires_at = datetime.utcnow() + timedelta(days=data.days_to_expire)

    new_api_key = ApiKey(
        name=data.name,
        prefix=db_prefix,
        hashed_key=hashed_key,
        expires_at=expires_at,
        user_id=user_id,
    )

    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)

    return new_api_key, final_key

async def get_user_by_api_key(
    db: AsyncSession, 
    api_key: str
) -> User | None:
    
    if not api_key.startswith(KEY_PREFIX) or '.' not in api_key:
        return None

    try:
        prefix_extracted = api_key.split('.')[0]
    except IndexError:
        return None

    cache_key = f"api_key:{prefix_extracted}"

    cached_data = await redis_client.get(cache_key)

    if cached_data:
        data_dict = json.loads(cached_data)
        
        hashed_key_db = data_dict.get("hashed_key")
        user_id = data_dict.get("user_id")
        expires_at = data_dict.get("expires_at")

        if expires_at and datetime.fromtimestamp(expires_at) < datetime.utcnow():
            return None

        if not verify_password(api_key, hashed_key_db):
            return None

        return await db.get(User, user_id)

    stmt = (
        select(ApiKey)
        .options(joinedload(ApiKey.user))
        .where(
            ApiKey.prefix == prefix_extracted,
            ApiKey.is_active is True
        )
    )

    result = await db.execute(stmt)
    api_key_db = result.scalar_one_or_none()

    if not api_key_db:
        return None

    if api_key_db.expires_at and api_key_db.expires_at < datetime.utcnow():
        return None

    if not verify_password(api_key, api_key_db.hashed_key):
        return None

    cache_payload = {
        "hashed_key": api_key_db.hashed_key,
        "user_id": api_key_db.user_id,
        "expires_at": api_key_db.expires_at.timestamp() if api_key_db.expires_at else None,
    }

    await redis_client.set(cache_key, json.dumps(cache_payload), ex=CACHE_TTL)

    return api_key_db.user

async def disable_api_key(
    db: AsyncSession,
    api_key_id: int,
    user: User,
) -> ApiKey | None :

    api_key = await db.get(ApiKey, api_key_id)

    if not api_key:
        return None

    if api_key.user_id != user.id and user.role != UserRole.ADMIN :
        return None

    api_key.is_active = False
    await db.commit()
    await db.refresh(api_key)
    await redis_client.delete(f"api_key:{api_key.prefix}")

    return api_key
