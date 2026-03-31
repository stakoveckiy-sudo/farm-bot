"""
Клавиатуры для админ-панели
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Модерация продавцов", callback_data="admin_sellers")],
        [InlineKeyboardButton(text="📦 Модерация товаров", callback_data="admin_products")],
        [InlineKeyboardButton(text="🗺️ География", callback_data="admin_geo")],
        [InlineKeyboardButton(text="📋 Справочники", callback_data="admin_dictionaries")],
        [InlineKeyboardButton(text="💳 Реквизиты оплаты", callback_data="admin_requisites")],
        [InlineKeyboardButton(text="📢 Рассылка всем", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
    ])


def get_moderation_sellers_menu(pending_count: int) -> InlineKeyboardMarkup:
    """Меню модерации продавцов"""
    status = f"На модерации: {pending_count}" if pending_count > 0 else "Нет на модерации"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📋 {status}", callback_data="mod_sellers_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_seller_moderation_actions() -> InlineKeyboardMarkup:
    """Действия при модерации продавца"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data="mod_seller_approve")],
        [InlineKeyboardButton(text="🔧 На доработку", callback_data="mod_seller_needs_fix")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data="mod_seller_reject")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_sellers")],
    ])


def get_product_moderation_actions() -> InlineKeyboardMarkup:
    """Действия при модерации товара"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data="mod_product_approve")],
        [InlineKeyboardButton(text="🔧 На доработку", callback_data="mod_product_needs_fix")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data="mod_product_reject")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_products")],
    ])


def get_geo_menu() -> InlineKeyboardMarkup:
    """Меню географии"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Страны", callback_data="admin_geo_countries")],
        [InlineKeyboardButton(text="🗺️ Регионы", callback_data="admin_geo_regions")],
        [InlineKeyboardButton(text="🏙️ Города", callback_data="admin_geo_cities")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_dictionaries_menu() -> InlineKeyboardMarkup:
    """Меню справочников"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Наименования товаров", callback_data="admin_dict_products")],
        [InlineKeyboardButton(text="📄 Формы юрлица", callback_data="admin_dict_legal_forms")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_requisites_menu() -> InlineKeyboardMarkup:
    """Меню реквизитов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить реквизиты", callback_data="admin_req_add")],
        [InlineKeyboardButton(text="📋 Список реквизитов", callback_data="admin_req_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_broadcast_menu() -> InlineKeyboardMarkup:
    """Меню рассылки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Отправить сообщение всем", callback_data="admin_broadcast_send")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_settings_menu() -> InlineKeyboardMarkup:
    """Меню настроек"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Паспортная проверка", callback_data="admin_set_passport")],
        [InlineKeyboardButton(text="⚖️ Лимиты (FREE/PRO)", callback_data="admin_set_limits")],
        [InlineKeyboardButton(text="🔔 Напоминания об оплате", callback_data="admin_set_reminders")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def get_approve_reject_menu() -> InlineKeyboardMarkup:
    """Кнопки подтверждения/отклонения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, подтвердить", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])