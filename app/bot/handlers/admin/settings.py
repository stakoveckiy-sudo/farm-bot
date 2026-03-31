"""
Настройки платформы - админ
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.bot.filters.is_admin import IsAdmin
from app.bot.keyboards.admin import get_settings_menu

router = Router()


@router.callback_query(F.data == "admin_settings", IsAdmin())
async def settings_menu(callback: CallbackQuery):
    """Меню настроек"""
    # TODO: Реализовать настройки
    await callback.message.edit_text(
        "⚙️ <b>Настройки платформы</b>\n\n"
        "🚧 Функция в разработке",
        reply_markup=get_settings_menu()
    )
    await callback.answer()