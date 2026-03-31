"""
FSM для создания витрины
"""
from aiogram.fsm.state import State, StatesGroup


class ShowcaseCreateForm(StatesGroup):
    """Состояния создания витрины"""
    
    waiting_for_name = State()  # Название витрины
    waiting_for_country = State()  # Страна
    waiting_for_region = State()  # Регион
    waiting_for_city = State()  # Город (опционально)
    waiting_for_trading_type = State()  # Опт/Розница
    waiting_for_delivery = State()  # Доставка: Да/Нет
    waiting_for_pickup_address = State()  # Адрес самовывоза (если доставка Нет)
    waiting_for_phone = State()  # Телефон витрины
    waiting_for_logo = State()  # Логотип (фото, опционально)
    waiting_for_description = State()  # Описание (опционально)
    waiting_for_confirmation = State()  # Подтверждение перед созданием