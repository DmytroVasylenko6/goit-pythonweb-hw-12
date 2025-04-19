from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.conf.config import settings

import logging

logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

SQLALCHEMY_DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to provide an asynchronous database session.

    This function yields an async session that ensures proper resource
    management using a context manager.

    Yields:
        AsyncSession: SQLAlchemy asynchronous session instance.
    """
    async with AsyncSessionLocal() as session:
        yield session
