"""
Async SQLAlchemy database setup.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.models.base import Base  # ← Импортируем Base из models

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database (create all tables)."""
    # Импортируем все модели чтобы они зарегистрировались в MetaData
    from src.models.user import User          # [web:17]
    from src.models.account import Account    # [web:22]
    from src.models.category import Category  # [web:22]
    from src.models.transaction import Transaction  # [web:22]
    from src.models.budget import Budget      # если есть такая модель

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

