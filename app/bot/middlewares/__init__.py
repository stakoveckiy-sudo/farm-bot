"""
Middleware для бота
"""
from app.bot.middlewares.db import DatabaseMiddleware

__all__ = ["DatabaseMiddleware"]