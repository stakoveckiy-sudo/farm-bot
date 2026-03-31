"""
Модерация товаров (админ)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.keyboards.admin import get_moderation_sellers_menu
from app.bot.filters.is_admin import IsAdmin
from app.db.repositories.product import ProductRepository

router = Router()


@router.callback_query(F.data == "admin_products", IsAdmin())
async def moderate_products(callback: CallbackQuery, session: AsyncSession):
    """Модерация товаров"""
    product_repo = ProductRepository(session)
    
    pending = await product_repo.get_pending_products()
    
    text = f"📦 <b>Модерация товаров</b>\n\nЖдут проверки: {len(pending)}"
    
    await callback.message.edit_text(text, reply_markup=get_moderation_sellers_menu(len(pending)))
    await callback.answer()