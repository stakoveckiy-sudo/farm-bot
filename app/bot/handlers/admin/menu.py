"""
Главное меню администратора
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.admin import get_admin_menu
from app.bot.filters.is_admin import IsAdmin

router = Router()


@router.callback_query(F.data == "admin_menu", IsAdmin())
async def admin_menu(callback: CallbackQuery):
    """Главное меню админа"""
    await callback.message.edit_text(
        "⚙️ <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()