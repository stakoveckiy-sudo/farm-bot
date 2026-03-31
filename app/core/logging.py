"""
Логирование (loguru + structlog)
"""
import sys
from loguru import logger
from .settings.config import Config


def setup_logging():
    """Инициализация логирования"""
    
    # Удаляем дефолтный хендлер
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=Config.LOG_LEVEL,
        colorize=True,
    )
    
    # File logging (если не debug)
    if not Config.DEBUG:
        logger.add(
            "/var/log/farmstore/app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="500 MB",
            retention="7 days",
        )
        
        # Отдельный лог для ошибок
        logger.add(
            "/var/log/farmstore/error.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="500 MB",
            retention="14 days",
        )
    
    return logger


# Инстанс логгера
app_logger = setup_logging()