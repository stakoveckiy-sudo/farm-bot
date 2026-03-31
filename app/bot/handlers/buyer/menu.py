"""
Меню покупателя
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.buyer import get_buyer_menu, get_search_menu

router = Router()


@router.callback_query(F.data == "buyer_menu")
async def buyer_menu(callback: CallbackQuery):
    """Главное меню покупателя"""
    await callback.message.edit_text(
        "🛍️ <b>Меню покупателя</b>\n\nЧто вы хотите сделать?",
        reply_markup=get_buyer_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "buyer_search")
async def search_products(callback: CallbackQuery):
    """Поиск товаров"""
    await callback.message.edit_text(
        "🔍 <b>Поиск товаров</b>\n\nВыберите параметры поиска или просмотрите каталог:",
        reply_markup=get_search_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "buyer_favorites")
async def favorites(callback: CallbackQuery):
    """Избранное"""
    await callback.message.edit_text(
        "❤️ <b>Избранное</b>\n\nЗдесь будут ваши избранные товары.",
    )
    await callback.answer()