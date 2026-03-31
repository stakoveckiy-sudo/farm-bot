"""
Рассылка сообщений - админ
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.bot.filters.is_admin import IsAdmin
from app.bot.keyboards.admin import get_broadcast_menu

router = Router()


@router.callback_query(F.data == "admin_broadcast", IsAdmin())
async def broadcast_menu(callback: CallbackQuery):
    """Меню рассылки"""
    # TODO: Реализовать рассылку
    await callback.message.edit_text(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "🚧 Функция в разработке",
        reply_markup=get_broadcast_menu()
    )
    await callback.answer()