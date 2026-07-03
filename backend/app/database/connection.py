"""Database connection manager with async session support."""

import time
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

logger = structlog.get_logger()

# Create async engine.
#
# ``pool_pre_ping`` is disabled: it adds a round-trip (SELECT 1) before
# every checkout, which roughly doubles latency for single-query
# endpoints. asyncpg already detects stale connections lazily and the
# pool recycles them on error.
#
# ``statement_timeout`` is set at the server level per connection so a
# runaway aggregation over a huge date range fails fast (HTTP 500 with
# a clear log) instead of holding a connection indefinitely.
# ``connect_timeout`` bounds the TCP connection establishment so a
# unreachable RDS host fails fast instead of hanging the request.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=10,
    connect_args={
        "timeout": 10,
        "server_settings": {
            "statement_timeout": "30000",
            "application_name": "llm-spend-api",
        },
    },
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database connection."""
    logger.info("Initializing database connection", url=settings.database_url.split("@")[-1])


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency for FastAPI."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
