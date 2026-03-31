"""
Главная точка входа приложения
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from loguru import logger
import os

from app.core.settings.config import Config
from app.core.logging import setup_logging
from app.web.server import create_webhook_server
from app.db.engine import init_db, create_engine, create_session_maker
from app.db.session import set_session_maker
from app.bot.router import get_main_router
from app.bot.middlewares.db import DatabaseMiddleware


async def main():
    """Главная функция запуска"""
    
    # === Setup logging ===
    setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск FarmStore Bot")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Log level: {Config.LOG_LEVEL}")
    logger.info("=" * 60)
    
    # === Создаём директории для хранилища ===
    os.makedirs(Config.STORAGE.images_path, exist_ok=True)
    logger.info(f"Storage path: {Config.STORAGE.root_path}")
    
    # === Setup Database ===
    logger.info("Инициализация БД...")
    engine = create_engine()
    
    # Создаём все таблицы (если их нет)
    async with engine.begin() as conn:
        await init_db(conn)
    
    logger.info("✓ БД готова")
    
    # Сессия для работы с БД
    session_maker = create_session_maker(engine)
    set_session_maker(session_maker)
    
    # === Setup Redis ===
    logger.info("Подключение к Redis...")
    try:
        redis = Redis(
            host=Config.REDIS.host,
            port=Config.REDIS.port,
            db=Config.REDIS.db,
            password=Config.REDIS.password if Config.REDIS.password else None,
            decode_responses=False,
        )
        # Проверяем подключение
        await redis.ping()
        logger.info("✓ Redis готов")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
        raise
    
    # === Setup Aiogram ===
    logger.info("Инициализация aiogram Bot и Dispatcher...")
    
    # Storage для FSM в Redis
    storage = RedisStorage(redis=redis)
    
    # Bot
    bot = Bot(token=Config.BOT_TOKEN, parse_mode="HTML")
    
    # Dispatcher
    dp = Dispatcher(storage=storage)
    
    # Регистрируем middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    # Регистрируем все роутеры
    dp.include_router(get_main_router())
    
    logger.info("✓ Bot и Dispatcher готовы")
    
    # === Start Webhook Server ===
    logger.info(f"Запуск webhook сервера на {Config.BOT_SERVER_HOST}:{Config.BOT_SERVER_PORT}...")
    try:
        await create_webhook_server(bot, dp)
        logger.info("✓ Webhook сервер запущен")
        logger.info(f"✓ Webhook URL: {Config.WEBHOOK.full_url}")
    except Exception as e:
        logger.error(f"Ошибка при запуске webhook: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("✓✓✓ Bot успешно запущен! ✓✓✓")
    logger.info("=" * 60)
    
    # Держим событие loop живым
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Bot остановлен пользователем")
    finally:
        logger.info("Очистка ресурсов...")
        await bot.session.close()
        await redis.aclose()  # Используем aclose() вместо close()
        await engine.dispose()
        logger.info("✓ Ресурсы очищены")


if __name__ == "__main__":
    asyncio.run(main())
