"""
Работа с сессиями БД
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Глобальная переменная для хранения session_maker
_session_maker: Optional[async_sessionmaker] = None


def set_session_maker(session_maker: async_sessionmaker):
    """Устанавливаем session_maker"""
    global _session_maker
    _session_maker = session_maker


def get_session_maker() -> async_sessionmaker:
    """Получаем session_maker"""
    if _session_maker is None:
        raise RuntimeError("Session maker not initialized. Call set_session_maker first.")
    return _session_maker


async def get_session() -> AsyncSession:
    """Получаем сессию (для dependency injection)"""
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
