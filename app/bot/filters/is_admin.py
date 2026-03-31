"""
Фильтр для проверки, является ли пользователь администратором
"""
from aiogram.filters import BaseFilter
from aiogram.types import User
from app.core.settings.config import Config


class IsAdmin(BaseFilter):
    """Проверка, является ли пользователь администратором"""
    
    async def __call__(self, message_or_callback = None, user: User = None) -> bool:
        """
        Проверяем, входит ли user.id в список администраторов
        """
        if user is None:
            return False
        
        return user.id in Config.ADMIN_IDS