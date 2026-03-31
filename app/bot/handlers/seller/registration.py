"""
Обработчики регистрации продавца (FSM)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.fsm.seller_registration import SellerRegistrationForm
from app.bot.keyboards.common import get_cancel_button, get_yes_no, get_skip_and_cancel
from app.bot.keyboards.start import get_role_selection
from app.bot.utils.nav import (
    SELLER_REGISTRATION_START, SELLER_REGISTRATION_COMPANY_NAME,
    SELLER_REGISTRATION_LEGAL_FORM, SELLER_REGISTRATION_OWNER_NAME,
    SELLER_REGISTRATION_INN_UNP, SELLER_REGISTRATION_PASSPORT,
    SELLER_REGISTRATION_CERT, SELLER_REGISTRATION_PHONE,
    SELLER_REGISTRATION_CONFIRM, SELLER_REGISTERED,
    ERROR_INVALID_INPUT, ERROR_INVALID_FILE_TYPE, ERROR_FILE_TOO_LARGE
)
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.db.repositories.dictionaries import DictionaryRepository
from app.core.settings.config import Config

router = Router()


@router.callback_query(F.data == "seller_registration_start")
async def start_registration(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Начало регистрации продавца"""
    await callback.message.edit_text(SELLER_REGISTRATION_START, reply_markup=get_cancel_button())
    await state.set_state(SellerRegistrationForm.waiting_for_company_name)
    await callback.answer()


@router.message(SellerRegistrationForm.waiting_for_company_name)
async def process_company_name(message: Message, state: FSMContext):
    """Обработка названия компании"""
    if not message.text or len(message.text) < 2:
        await message.answer(ERROR_INVALID_INPUT)
        return
    
    await state.update_data(company_name=message.text)
    
    # Переходим к выбору формы юрлица
    await state.set_state(SellerRegistrationForm.waiting_for_legal_form)
    await message.answer(SELLER_REGISTRATION_LEGAL_FORM)


@router.callback_query(SellerRegistrationForm.waiting_for_legal_form)
async def process_legal_form(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработка формы юрлица (выбор из справочника)"""
    dict_repo = DictionaryRepository(session)
    legal_forms = await dict_repo.get_all_legal_forms()
    
    if callback.data.startswith("legal_form_"):
        form_id = int(callback.data.split("_")[2])
        await state.update_data(legal_form_id=form_id)
        
        # Переходим к ФИО
        await state.set_state(SellerRegistrationForm.waiting_for_owner_name)
        await callback.message.edit_text(SELLER_REGISTRATION_OWNER_NAME, reply_markup=get_cancel_button())
        await callback.answer()


@router.message(SellerRegistrationForm.waiting_for_owner_name)
async def process_owner_name(message: Message, state: FSMContext):
    """Обработка ФИО владельца"""
    if not message.text or len(message.text) < 3:
        await message.answer(ERROR_INVALID_INPUT)
        return
    
    await state.update_data(owner_name=message.text)
    
    # Переходим к ИНН/УНП
    await state.set_state(SellerRegistrationForm.waiting_for_inn_unp)
    await message.answer("🔢 ИНН/УНП\n\nВведите ИНН (для РФ) или УНП (для РБ):", reply_markup=get_cancel_button())


@router.message(SellerRegistrationForm.waiting_for_inn_unp)
async def process_inn_unp(message: Message, state: FSMContext):
    """Обработка ИНН/УНП"""
    if not message.text or len(message.text) < 5:
        await message.answer(ERROR_INVALID_INPUT)
        return
    
    await state.update_data(inn_unp=message.text)
    
    # Переходим к паспорту
    await state.set_state(SellerRegistrationForm.waiting_for_passport)
    await message.answer(SELLER_REGISTRATION_PASSPORT, reply_markup=get_cancel_button())


@router.message(SellerRegistrationForm.waiting_for_passport, F.photo)
async def process_passport(message: Message, state: FSMContext):
    """Обработка фото паспорта"""
    photo = message.photo[-1]
    
    # Проверяем размер
    if photo.file_size and photo.file_size > Config.STORAGE.max_file_size:
        await message.answer(ERROR_FILE_TOO_LARGE)
        return
    
    # Сохраняем file_id
    await state.update_data(passport_file_id=photo.file_id)
    
    # Переходим к свидетельству
    await state.set_state(SellerRegistrationForm.waiting_for_registration_cert)
    await message.answer(SELLER_REGISTRATION_CERT, reply_markup=get_cancel_button())


@router.message(SellerRegistrationForm.waiting_for_passport)
async def process_passport_invalid(message: Message):
    """Неверный формат для паспорта"""
    await message.answer(ERROR_INVALID_FILE_TYPE)


@router.message(SellerRegistrationForm.waiting_for_registration_cert, F.photo)
async def process_registration_cert(message: Message, state: FSMContext):
    """Обработка фото свидетельства о регистрации"""
    photo = message.photo[-1]
    
    # Проверяем размер
    if photo.file_size and photo.file_size > Config.STORAGE.max_file_size:
        await message.answer(ERROR_FILE_TOO_LARGE)
        return
    
    # Сохраняем file_id
    await state.update_data(registration_cert_file_id=photo.file_id)
    
    # Переходим к телефону
    await state.set_state(SellerRegistrationForm.waiting_for_owner_phone)
    await message.answer(SELLER_REGISTRATION_PHONE, reply_markup=get_cancel_button())


@router.message(SellerRegistrationForm.waiting_for_registration_cert)
async def process_registration_cert_invalid(message: Message):
    """Неверный формат для свидетельства"""
    await message.answer(ERROR_INVALID_FILE_TYPE)


@router.message(SellerRegistrationForm.waiting_for_owner_phone)
async def process_owner_phone(message: Message, state: FSMContext):
    """Обработка телефона владельца"""
    # Простая валидация телефона
    phone = message.text.strip()
    if not phone or len(phone) < 10:
        await message.answer("❌ Неверный номер телефона. Используйте формат: +7 (999) 123-45-67")
        return
    
    await state.update_data(owner_phone=phone)
    
    # Переходим к подтверждению
    await state.set_state(SellerRegistrationForm.waiting_for_confirmation)
    
    data = await state.get_data()
    
    confirm_text = f"""
✅ <b>Проверка данных</b>

Пожалуйста, проверьте введённые данные:

<b>Компания:</b> {data.get('company_name')}
<b>ФИО:</b> {data.get('owner_name')}
<b>ИНН/УНП:</b> {data.get('inn_unp')}
<b>Телефон:</b> {data.get('owner_phone')}

Все верно?
"""
    
    await message.answer(confirm_text, reply_markup=get_yes_no())


@router.callback_query(SellerRegistrationForm.waiting_for_confirmation, F.data == "yes")
async def confirm_registration(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение регистрации"""
    data = await state.get_data()
    
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    # Обновляем данные продавца
    try:
        await seller_repo.update_registration_data(
            user_id=user.id,
            company_name=data.get('company_name'),
            legal_form_id=data.get('legal_form_id'),
            owner_name=data.get('owner_name'),
            inn_unp=data.get('inn_unp'),
            owner_phone=data.get('owner_phone'),
            passport_file=data.get('passport_file_id'),
            registration_cert_file=data.get('registration_cert_file_id'),
        )
        
        logger.info(f"Seller registered: {callback.from_user.id}")
        
        await callback.message.edit_text(SELLER_REGISTERED, reply_markup=get_role_selection())
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error during seller registration: {e}")
        await callback.message.edit_text("❌ Ошибка при сохранении. Попробуйте позже.", reply_markup=get_cancel_button())
    
    await callback.answer()


@router.callback_query(SellerRegistrationForm.waiting_for_confirmation, F.data == "no")
async def reject_confirmation(callback: CallbackQuery, state: FSMContext):
    """Отмена подтверждения, возврат к редактированию"""
    await callback.message.edit_text(SELLER_REGISTRATION_COMPANY_NAME, reply_markup=get_cancel_button())
    await state.set_state(SellerRegistrationForm.waiting_for_company_name)
    await callback.answer()


@router.callback_query(F.data == "cancel", StateFilter(SellerRegistrationForm))
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Отмена регистрации"""
    await state.clear()
    await callback.message.edit_text("❌ Регистрация отменена.", reply_markup=get_role_selection())
    await callback.answer()