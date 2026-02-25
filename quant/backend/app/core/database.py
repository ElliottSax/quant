"""Database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import settings

# Detect if using SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create async engine with optimized pool settings
if is_sqlite:
    # SQLite: use StaticPool for single connection (required for SQLite)
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
elif settings.ENVIRONMENT == "test":
    # Test environment: use NullPool and no pool parameters
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        future=True,
        poolclass=NullPool,
    )
else:
    # Production/development with PostgreSQL: use connection pooling
    # Pool settings can be overridden via environment variables:
    # - DATABASE_POOL_SIZE (default: 20)
    # - DATABASE_MAX_OVERFLOW (default: 40)
    # - DATABASE_POOL_RECYCLE_SECONDS (default: 3600)
    # - SECURITY_DB_POOL_TIMEOUT_SECONDS (default: 30)
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        future=True,
        # Connection pool configuration for better concurrency
        pool_size=settings.database.POOL_SIZE,
        max_overflow=settings.database.MAX_OVERFLOW,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=settings.database.POOL_RECYCLE_SECONDS,
        pool_timeout=settings.security.DB_POOL_TIMEOUT_SECONDS,
    )

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
