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
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        future=True,
        # Connection pool configuration for better concurrency
        pool_size=20,  # Increased from default 5
        max_overflow=40,  # Increased from default 10
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_timeout=30,  # Wait up to 30s for connection
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
