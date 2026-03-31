"""
Webhook сервер для Telegram бота
"""
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from loguru import logger
import secrets

from app.core.settings.config import Config
from app.db.session import get_session_maker


class WebhookServer:
    """Webhook сервер"""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Регистрируем маршруты"""
        self.app.router.add_post(Config.WEBHOOK.path, self._webhook_handler)
        self.app.router.add_get("/health", self._health_check)
    
    async def _webhook_handler(self, request: web.Request) -> web.Response:
        """Обработчик webhook"""
        try:
            data = await request.json()
            update = Update(**data)
            
            # Получаем session_maker и создаём сессию для обработки
            session_maker = get_session_maker()
            async with session_maker() as session:
                # Передаём session в контексте диспетчера
                await self.dp.feed_update(
                    self.bot, 
                    update,
                    session=session  # Передаём сессию
                )
            
            return web.Response(status=200, text="OK")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return web.Response(status=400, text="Bad Request")
    
    async def _health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.Response(status=200, text="OK")
    
    async def start(self):
        """Запустить сервер"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner,
            Config.BOT_SERVER_HOST,
            Config.BOT_SERVER_PORT
        )
        
        await site.start()
        logger.info(f"✓ Webhook сервер запущен на {Config.BOT_SERVER_HOST}:{Config.BOT_SERVER_PORT}")
        
        return runner


async def create_webhook_server(bot: Bot, dp: Dispatcher) -> web.AppRunner:
    """Создание и запуск webhook сервера"""
    server = WebhookServer(bot, dp)
    runner = await server.start()
    
    # Генерируем безопасный secret token
    secret_token = secrets.token_urlsafe(32)
    
    # Устанавливаем webhook на Telegram
    try:
        await bot.set_webhook(
            url=Config.WEBHOOK.full_url,
            secret_token=secret_token
        )
        logger.info(f"✓ Webhook установлен: {Config.WEBHOOK.full_url}")
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}")
        logger.warning("Продолжаем работу без webhook")
    
    return runner
