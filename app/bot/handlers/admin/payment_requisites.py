"""
Управление реквизитами для оплаты - админ
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.bot.filters.is_admin import IsAdmin
from app.bot.keyboards.admin import get_requisites_menu

router = Router()


@router.callback_query(F.data == "admin_requisites", IsAdmin())
async def requisites_menu(callback: CallbackQuery):
    """Меню реквизитов"""
    # TODO: Реализовать управление реквизитами
    await callback.message.edit_text(
        "💳 <b>Реквизиты для оплаты</b>\n\n"
        "🚧 Функция в разработке",
        reply_markup=get_requisites_menu()
    )
    await callback.answer()