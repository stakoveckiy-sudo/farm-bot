"""
Стартовый обработчик (/start команда и выбор роли)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.keyboards.start import get_role_selection, get_admin_panel
from app.bot.keyboards.seller import get_seller_menu
from app.bot.keyboards.buyer import get_buyer_menu
from app.bot.keyboards.common import get_home_button
from app.bot.utils.nav import WELCOME_TEXT
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.core.settings.config import Config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обработчик команды /start"""
    
    # Создаём или получаем пользователя
    user_repo = UserRepository(session)
    user = await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        username=message.from_user.username,
    )
    
    # Проверяем, админ ли
    if user.telegram_id in Config.ADMIN_IDS:
        user = await user_repo.set_admin_role(user.id)
    
    logger.info(f"User started: {message.from_user.id}")
    
    # Отправляем приветствие с выбором роли
    keyboard = get_role_selection()
    
    # Если админ — добавляем кнопку админ-панели
    if user.is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")
        ])
    
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)


@router.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery, session: AsyncSession):
    """Возврат в главное меню (выбор роли)"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    keyboard = get_role_selection()
    
    if user and user.is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")
        ])
    
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "role_seller")
async def select_seller_role(callback: CallbackQuery, session: AsyncSession):
    """Выбрана роль продавца"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    # Добавляем роль
    await user_repo.set_seller_role(user.id)
    
    # Получаем/создаём профиль продавца
    seller_repo = SellerRepository(session)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        seller = await seller_repo.create(user.id)
    
    logger.info(f"User selected seller role: {callback.from_user.id}")
    
    # Показываем меню продавца
    status_key = seller.status.value if hasattr(seller.status, 'value') else seller.status
    keyboard = get_seller_menu(status_key)
    
    await callback.message.edit_text(
        "🛒 <b>Меню продавца</b>\n\nЧто вы хотите сделать?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "role_buyer")
async def select_buyer_role(callback: CallbackQuery, session: AsyncSession):
    """Выбрана роль покупателя"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    # Добавляем роль
    await user_repo.set_buyer_role(user.id)
    
    logger.info(f"User selected buyer role: {callback.from_user.id}")
    
    # Показываем меню покупателя
    keyboard = get_buyer_menu()
    
    await callback.message.edit_text(
        "🛍️ <b>Меню покупателя</b>\n\nЧто вы хотите сделать?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Показываем справку"""
    help_text = """
❓ <b>Как это работает?</b>

<b>Для продавцов:</b>
1. Зарегистрируйтесь и заполните данные компании
2. Создайте витрину (магазин)
3. Добавьте товары с описанием и ценой
4. Ваши товары появятся в поиске покупателей
5. Общайтесь с покупателями напрямую

<b>Для покупателей:</b>
1. Используйте поиск для нахождения товаров
2. Выберите нужный товар и продавца
3. Свяжитесь с продавцом (телефон или Telegram)
4. Договоритесь о цене и доставке

<b>Платные функции:</b>
• <b>Бесплатно:</b> 1 витрина, 5 товаров
• <b>PRO (30 дней):</b> до 5 витрин, до 100 товаров в каждой

Платежи идут через реквизиты. Вся информация конфиденциальна! 🔒
"""
    
    await callback.message.edit_text(help_text, reply_markup=get_home_button())
    await callback.answer()


@router.callback_query(F.data == "admin_panel")
async def enter_admin_panel(callback: CallbackQuery, session: AsyncSession):
    """Вход в админ-панель"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_admin:
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    from app.bot.keyboards.admin import get_admin_menu
    
    await callback.message.edit_text(
        "⚙️ <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()
