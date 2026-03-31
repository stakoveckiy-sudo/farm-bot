"""
Модерация продавцов (админ)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.keyboards.admin import get_moderation_sellers_menu, get_seller_moderation_actions
from app.bot.filters.is_admin import IsAdmin
from app.db.repositories.seller import SellerRepository
from app.db.models.seller_profile import SellerStatus

router = Router()


@router.callback_query(F.data == "admin_sellers", IsAdmin())
async def moderate_sellers(callback: CallbackQuery, session: AsyncSession):
    """Модерация продавцов"""
    seller_repo = SellerRepository(session)
    
    pending = await seller_repo.get_pending_sellers()
    
    keyboard = get_moderation_sellers_menu(len(pending))
    
    await callback.message.edit_text(
        f"👥 <b>Модерация продавцов</b>\n\nЖдут проверки: {len(pending)}",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "mod_sellers_list", IsAdmin())
async def list_pending_sellers(callback: CallbackQuery, session: AsyncSession):
    """Список продавцов на модерации"""
    seller_repo = SellerRepository(session)
    
    pending = await seller_repo.get_pending_sellers()
    
    if not pending:
        await callback.message.edit_text("✅ Нет продавцов на модерации", reply_markup=get_moderation_sellers_menu(0))
        await callback.answer()
        return
    
    text = "📋 <b>Продавцы на модерации:</b>\n\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for seller in pending:
        text += f"• {seller.company_name} ({seller.owner_name})\n"
        buttons.append([InlineKeyboardButton(text=f"🔍 {seller.company_name}", callback_data=f"mod_seller_view:{seller.id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("mod_seller_view:"), IsAdmin())
async def view_seller_for_moderation(callback: CallbackQuery, session: AsyncSession):
    """Просмотр данных продавца для модерации"""
    seller_id = int(callback.data.split(":")[1])
    
    seller_repo = SellerRepository(session)
    seller = await seller_repo.get_by_id(seller_id)
    
    if not seller:
        await callback.answer("❌ Продавец не найден", show_alert=True)
        return
    
    text = f"""
📋 <b>Данные продавца</b>

<b>Компания:</b> {seller.company_name}
<b>ФИО:</b> {seller.owner_name}
<b>Форма:</b> {seller.legal_form.name if seller.legal_form else "—"}
<b>ИНН/УНП:</b> {seller.inn_unp}
<b>Телефон:</b> {seller.owner_phone}

<b>Документы:</b>
• Паспорт: {'загружен' if seller.passport_file else 'не загружен'}
• Свидетельство: {'загружен' if seller.registration_cert_file else 'не загружен'}

<b>Статус:</b> {seller.status.value}
"""
    
    keyboard = get_seller_moderation_actions()
    
    # Сохраняем seller_id в callback_data для дальнейших действий
    await callback.message.edit_text(text, reply_markup=keyboard)
    # TODO: Сохранить seller_id в контексте
    await callback.answer()


@router.callback_query(F.data == "mod_seller_approve", IsAdmin())
async def approve_seller(callback: CallbackQuery, session: AsyncSession):
    """Одобрить продавца"""
    # TODO: Получить seller_id из контекста
    seller_id = 1  # Временно
    
    seller_repo = SellerRepository(session)
    seller = await seller_repo.approve_seller(seller_id)
    
    logger.info(f"Seller approved by admin: {seller_id}")
    
    await callback.message.edit_text(
        f"✅ <b>Продавец одобрен!</b>\n\n{seller.company_name}",
        reply_markup=get_moderation_sellers_menu(0)
    )
    await callback.answer()


@router.callback_query(F.data == "mod_seller_needs_fix", IsAdmin())
async def seller_needs_fix(callback: CallbackQuery):
    """Отправить продавца на доработку"""
    await callback.message.edit_text(
        "💬 Введите комментарий для продавца:",
        reply_markup=F.cancel_button
    )
    # TODO: FSM для комментария
    await callback.answer()


@router.callback_query(F.data == "mod_seller_reject", IsAdmin())
async def reject_seller(callback: CallbackQuery):
    """Отклонить продавца"""
    await callback.message.edit_text(
        "💬 Введите причину отклонения:",
        reply_markup=F.cancel_button
    )
    # TODO: FSM для причины отклонения
    await callback.answer()