"""SQLAlchemy async engine and session factory."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
)

from bot.config import settings
from bot.database.base import Base

_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db() -> None:
    global _engine, _session_maker

    logger.info(f"🗄 Initializing database")

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    _session_maker = async_sessionmaker(
        bind=_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.success("✅ Database ready")


async def close_db() -> None:
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("🗄 Database closed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not _session_maker:
        raise RuntimeError("Database not initialized")
    async with _session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise