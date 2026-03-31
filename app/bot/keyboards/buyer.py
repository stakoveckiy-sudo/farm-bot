"""
Клавиатуры для покупателя
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_buyer_menu() -> InlineKeyboardMarkup:
    """Главное меню покупателя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Найти товар", callback_data="buyer_search")],
        [InlineKeyboardButton(text="❤️ Избранное", callback_data="buyer_favorites")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")],
    ])


def get_search_menu() -> InlineKeyboardMarkup:
    """Меню поиска"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Начать поиск", callback_data="search_start")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="buyer_menu")],
    ])


def get_product_card_menu() -> InlineKeyboardMarkup:
    """Меню карточки товара"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Позвонить", callback_data="contact_call")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data="contact_telegram")],
        [InlineKeyboardButton(text="🏪 Открыть витрину", callback_data="open_showcase")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def get_contact_menu(has_phone: bool = True, has_telegram: bool = True) -> InlineKeyboardMarkup:
    """Варианты контакта с продавцом"""
    buttons = []
    
    if has_phone:
        buttons.append([InlineKeyboardButton(text="☎️ Позвонить продавцу", callback_data="contact_call")])
    
    if has_telegram:
        buttons.append([InlineKeyboardButton(text="💬 Написать в Telegram", callback_data="contact_telegram")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)