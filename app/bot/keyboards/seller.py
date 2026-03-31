"""
Клавиатуры для продавца
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_seller_menu(seller_status: str) -> InlineKeyboardMarkup:
    """Главное меню продавца (в зависимости от статуса)"""
    
    if seller_status == "none":
        # Ещё не регался
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Заполнить данные", callback_data="seller_registration_start")],
            [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
        ])
    
    elif seller_status == "pending":
        # На модерации
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои отправленные данные", callback_data="seller_view_data")],
            [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
        ])
    
    elif seller_status == "needs_fix":
        # На доработку
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Исправить данные", callback_data="seller_registration_start")],
            [InlineKeyboardButton(text="💬 Комментарий модератора", callback_data="seller_view_comment")],
            [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
        ])
    
    elif seller_status == "approved":
        # Одобрен
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏪 Мои витрины", callback_data="seller_showcases")],
            [InlineKeyboardButton(text="📦 Мои товары", callback_data="seller_products")],
            [InlineKeyboardButton(text="💳 Подписка/Оплата", callback_data="seller_subscription")],
            [InlineKeyboardButton(text="👤 Профиль продавца", callback_data="seller_profile")],
            [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
        ])
    
    elif seller_status == "blocked":
        # Заблокирован
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Подписка/Оплата", callback_data="seller_subscription")],
            [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
        ])
    
    # По умолчанию (rejected или неизвестный)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Попробовать снова", callback_data="seller_registration_start")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
    ])


def get_seller_registration_menu() -> InlineKeyboardMarkup:
    """Меню регистрации продавца"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Начать заполнение", callback_data="seller_reg_start")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="home")],
    ])


def get_showcases_menu(showcase_count: int, limit: int = 1) -> InlineKeyboardMarkup:
    """Меню витрин"""
    buttons = []
    
    if showcase_count < limit:
        buttons.append([InlineKeyboardButton(text="➕ Создать витрину", callback_data="showcase_create")])
    else:
        buttons.append([InlineKeyboardButton(text="⚠️ Лимит витрин достигнут", callback_data="showcase_limit")])
    
    buttons.append([InlineKeyboardButton(text="💳 Перейти на PRO", callback_data="seller_subscription")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="seller_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_showcase_actions(showcase_id: int) -> InlineKeyboardMarkup:
    """Действия с витриной"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Товары витрины", callback_data=f"showcase_products:{showcase_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"showcase_edit:{showcase_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"showcase_delete:{showcase_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="seller_showcases")],
    ])


def get_products_menu(product_count: int, limit: int = 5) -> InlineKeyboardMarkup:
    """Меню товаров"""
    buttons = []
    
    if product_count < limit:
        buttons.append([InlineKeyboardButton(text="➕ Добавить товар", callback_data="product_create")])
    else:
        buttons.append([InlineKeyboardButton(text="⚠️ Лимит товаров достигнут", callback_data="product_limit")])
    
    buttons.append([InlineKeyboardButton(text="💳 Перейти на PRO", callback_data="seller_subscription")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="seller_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_actions(product_id: int) -> InlineKeyboardMarkup:
    """Действия с товаром"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"product_edit:{product_id}")],
        [InlineKeyboardButton(text="📊 Обновить остаток", callback_data=f"product_update_stock:{product_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"product_delete:{product_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="seller_products")],
    ])


def get_subscription_menu(plan: str, expires_at: str = None) -> InlineKeyboardMarkup:
    """Меню подписки"""
    buttons = [[InlineKeyboardButton(text=f"📋 Текущий план: {plan}", callback_data="subscription_info")]]
    
    if plan == "free":
        buttons.append([InlineKeyboardButton(text="⬆️ Перейти на PRO", callback_data="subscription_upgrade")])
    else:
        buttons.append([InlineKeyboardButton(text="🔄 Продлить PRO", callback_data="subscription_renew")])
    
    buttons.append([InlineKeyboardButton(text="📈 Поднять в топ (неделя)", callback_data="subscription_boost")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="seller_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_menu() -> InlineKeyboardMarkup:
    """Меню оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Получить реквизиты", callback_data="payment_get_requisites")],
        [InlineKeyboardButton(text="📸 Я оплатил (загрузить чек)", callback_data="payment_upload_receipt")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="seller_subscription")],
    ])