"""
Инициализация движка SQLAlchemy и создание таблиц
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from loguru import logger

from app.core.settings.config import Config
from app.db.models import Base


async def init_db(connection):
    """Создаём все таблицы (если их нет)"""
    try:
        await connection.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_engine() -> AsyncEngine:
    """Создаём async engine"""
    return create_async_engine(
        Config.DB.url,
        echo=Config.DB.echo,
        pool_size=Config.DB.pool_size,
        max_overflow=Config.DB.max_overflow,
        poolclass=NullPool if Config.DEBUG else None,
    )


def create_session_maker(engine: AsyncEngine):
    """Создаём factory для сессий"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )