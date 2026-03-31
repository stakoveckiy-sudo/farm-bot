"""
FSM для регистрации продавца
"""
from aiogram.fsm.state import State, StatesGroup


class SellerRegistrationForm(StatesGroup):
    """Состояния заполнения профиля продавца"""
    
    # Основные данные
    waiting_for_company_name = State()  # Название компании
    waiting_for_legal_form = State()  # Форма юрлица (ООО/ИП/ЧП)
    waiting_for_owner_name = State()  # ФИО владельца
    waiting_for_inn_unp = State()  # ИНН/УНП
    
    # Документы
    waiting_for_passport = State()  # Фото паспорта
    waiting_for_registration_cert = State()  # Свидетельство о регистрации
    
    # Контакты
    waiting_for_owner_phone = State()  # Телефон владельца
    
    # Подтверждение
    waiting_for_confirmation = State()  # Подтверждение перед отправкой на модерацию