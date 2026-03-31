"""
Middleware для подключения БД к каждому запросу
"""
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session_maker


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для подключения БД"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Выполняем middleware"""
        session_maker = get_session_maker()
        
        async with session_maker() as session:
            data["session"] = session
            return await handler(event, data)
