"""
Меню продавца
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.bot.keyboards.seller import get_seller_menu
from app.bot.keyboards.common import get_home_button

router = Router()


@router.callback_query(F.data == "seller_menu")
async def seller_menu(callback: CallbackQuery, session: AsyncSession):
    """Главное меню продавца"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        await callback.answer("❌ Профиль продавца не найден", show_alert=True)
        return
    
    # Статус в виде строки
    status = seller.status.value if hasattr(seller.status, 'value') else str(seller.status)
    
    keyboard = get_seller_menu(status)
    
    await callback.message.edit_text(
        "🛒 <b>Меню продавца</b>",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "seller_view_data")
async def view_seller_data(callback: CallbackQuery, session: AsyncSession):
    """Просмотр данных продавца"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return
    
    text = f"""
📋 <b>Ваши данные</b>

<b>Статус:</b> {seller.status.value if hasattr(seller.status, 'value') else seller.status}

<b>Компания:</b> {seller.company_name or "—"}
<b>Форма:</b> {seller.legal_form.name if seller.legal_form else "—"}
<b>ФИО:</b> {seller.owner_name or "—"}
<b>ИНН/УНП:</b> {seller.inn_unp or "—"}
<b>Телефон:</b> {seller.owner_phone or "—"}

<b>Дата отправки:</b> {seller.created_at.strftime('%d.%m.%Y %H:%M') if seller.created_at else "—"}
"""
    
    await callback.message.edit_text(text, reply_markup=get_home_button())
    await callback.answer()


@router.callback_query(F.data == "seller_view_comment")
async def view_moderator_comment(callback: CallbackQuery, session: AsyncSession):
    """Просмотр комментария модератора"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller or not seller.moderator_comment:
        await callback.answer("❌ Комментариев нет", show_alert=True)
        return
    
    text = f"""
💬 <b>Комментарий модератора</b>

{seller.moderator_comment}

---

⚠️ Пожалуйста, исправьте указанные ошибки и отправьте данные снова.
"""
    
    await callback.message.edit_text(text, reply_markup=get_home_button())
    await callback.answer()


@router.callback_query(F.data == "seller_profile")
async def seller_profile(callback: CallbackQuery, session: AsyncSession):
    """Профиль продавца"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return
    
    text = f"""
👤 <b>Профиль продавца</b>

<b>Статус:</b> {seller.status.value if hasattr(seller.status, 'value') else seller.status}
<b>Компания:</b> {seller.company_name or "—"}
<b>ФИО:</b> {seller.owner_name or "—"}
<b>Телефон:</b> {seller.owner_phone or "—"}

<b>Членство:</b> С {seller.created_at.strftime('%d.%m.%Y') if seller.created_at else "—"}

Если нужно обновить данные, напишите администратору.
"""
    
    await callback.message.edit_text(text, reply_markup=get_home_button())
    await callback.answer()