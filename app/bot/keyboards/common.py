"""
Общие кнопки, используемые везде
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_home_button() -> InlineKeyboardMarkup:
    """Кнопка 'Домой' (возврат в главное меню)"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏠 Домой", callback_data="home")
    ]])


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад", callback_data="back")
    ]])


def get_home_and_back() -> InlineKeyboardMarkup:
    """Кнопки 'Назад' и 'Домой'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад", callback_data="back"),
        InlineKeyboardButton(text="🏠 Домой", callback_data="home"),
    ]])


def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка 'Отмена'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ]])


def get_yes_no() -> InlineKeyboardMarkup:
    """Кнопки 'Да/Нет'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Да", callback_data="yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="no"),
    ]])


def get_confirm_cancel() -> InlineKeyboardMarkup:
    """Кнопки 'Подтвердить/Отмена'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    ]])


def get_phone_request() -> ReplyKeyboardMarkup:
    """Запрос на отправку номера телефона"""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="📱 Отправить номер", request_contact=True)
        ]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_skip_button() -> InlineKeyboardMarkup:
    """Кнопка 'Пропустить'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip")
    ]])


def get_skip_and_cancel() -> InlineKeyboardMarkup:
    """Кнопки 'Пропустить' и 'Отмена'"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    ]])
