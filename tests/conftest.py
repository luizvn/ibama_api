import os
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.api import deps
from app.main import app
from app.models.base import Base
from app.models.infraction import Infraction  # noqa: F401
from app.models.user import User  # noqa: F401


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


TEST_DATABASE_URL = os.getenv("DATABASE_URL_TEST")
if not TEST_DATABASE_URL:
    raise ValueError("DATABASE_URL_TEST não está definida no ambiente")


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await db_engine.connect()

    trans = await connection.begin()

    SessionTest = async_sessionmaker(
        bind=connection, expire_on_commit=False, class_=AsyncSession
    )
    session = SessionTest()

    try:
        yield session
    finally:
        await session.close()

        await trans.rollback()

        await connection.close()


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[deps.get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    del app.dependency_overrides[deps.get_db]
