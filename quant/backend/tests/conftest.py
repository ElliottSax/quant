"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.politician import Politician
from app.models.trade import Trade

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    from sqlalchemy import event

    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLite doesn't support char_length() - register it as length()
    @event.listens_for(engine.sync_engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        # Register char_length as an alias for length in SQLite
        dbapi_connection.create_function('char_length', 1, len)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(db_session):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create test superuser."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPassword123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Create authentication token for test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_politician(db_session: AsyncSession) -> Politician:
    """Create test politician."""
    politician = Politician(
        name="John Doe",
        chamber="senate",
        party="Independent",
        state="CA",
        bioguide_id="D000001",
    )
    db_session.add(politician)
    await db_session.commit()
    await db_session.refresh(politician)
    return politician


@pytest.fixture
async def test_trade(db_session: AsyncSession, test_politician: Politician) -> Trade:
    """Create test trade."""
    from datetime import date
    from decimal import Decimal

    trade = Trade(
        politician_id=test_politician.id,
        ticker="AAPL",
        transaction_type="buy",
        amount_min=Decimal("1000.00"),
        amount_max=Decimal("15000.00"),
        transaction_date=date(2024, 1, 15),
        disclosure_date=date(2024, 2, 1),
        source_url="https://example.com/disclosure/123",
    )
    db_session.add(trade)
    await db_session.commit()
    await db_session.refresh(trade)
    return trade
