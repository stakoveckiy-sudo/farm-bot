"""
Клавиатуры для стартового меню (выбор роли)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_role_selection() -> InlineKeyboardMarkup:
    """Выбор роли: Продавец / Покупатель"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Я продавец", callback_data="role_seller"),
            InlineKeyboardButton(text="🛍️ Я покупатель", callback_data="role_buyer"),
        ],
        [
            InlineKeyboardButton(text="❓ Как это работает", callback_data="help"),
        ]
    ])


def get_admin_panel() -> InlineKeyboardMarkup:
    """Кнопка входа в админ-панель (для администраторов)"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")
    ]])