"""
FSM для добавления товара
"""
from aiogram.fsm.state import State, StatesGroup


class ProductCreateForm(StatesGroup):
    """Состояния добавления товара"""
    
    waiting_for_showcase = State()  # Выбор витрины
    waiting_for_product_name = State()  # Выбор наименования товара
    waiting_for_price = State()  # Цена за кг
    waiting_for_quantity = State()  # Количество в наличии
    waiting_for_image = State()  # Фото товара
    waiting_for_description = State()  # Описание (опционально)
    waiting_for_trading_type = State()  # Опт/Розница (опционально)
    waiting_for_confirmation = State()  # Подтверждение перед отправкой