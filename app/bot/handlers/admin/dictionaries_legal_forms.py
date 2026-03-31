"""
Управление справочником форм юрлица - админ
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.filters.is_admin import IsAdmin
from app.bot.keyboards.common import get_cancel_button
from app.db.repositories.dictionaries import DictionaryRepository

router = Router()


class LegalFormForms(StatesGroup):
    """FSM для форм юрлица"""
    waiting_for_name = State()
    waiting_for_code = State()


@router.callback_query(F.data == "admin_dict_legal_forms", IsAdmin())
async def list_legal_forms(callback: CallbackQuery, session: AsyncSession):
    """Список форм юрлица"""
    dict_repo = DictionaryRepository(session)
    forms = await dict_repo.get_all_legal_forms()
    
    if not forms:
        text = "📄 <b>Формы юрлица</b>\n\nЗаписей нет."
    else:
        text = "📄 <b>Формы юрлица</b>\n\n"
        for form in forms:
            text += f"• {form.name} ({form.code})\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить форму", callback_data="admin_dict_add_legal_form")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_dict_add_legal_form", IsAdmin())
async def add_legal_form(callback: CallbackQuery, state: FSMContext):
    """Добавить форму юрлица"""
    await callback.message.edit_text(
        "📝 Введите название формы (например: ООО, ИП, ЧП):",
        reply_markup=get_cancel_button()
    )
    await state.set_state(LegalFormForms.waiting_for_name)
    await callback.answer()


@router.message(LegalFormForms.waiting_for_name, IsAdmin())
async def process_legal_form_name(message: Message, state: FSMContext):
    """Обработка названия формы"""
    await state.update_data(form_name=message.text)
    await state.set_state(LegalFormForms.waiting_for_code)
    await message.answer(
        "🔤 Введите код формы (например: LLC, IP, CP):",
        reply_markup=get_cancel_button()
    )


@router.message(LegalFormForms.waiting_for_code, IsAdmin())
async def process_legal_form_code(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка кода формы"""
    data = await state.get_data()
    
    dict_repo = DictionaryRepository(session)
    form = await dict_repo.create_legal_form(
        name=data['form_name'],
        code=message.text.upper()
    )
    
    logger.info(f"Legal form created: {form.id}")
    
    await message.answer(
        f"✅ <b>Форма добавлена!</b>\n\n{form.name} ({form.code})",
        reply_markup=get_cancel_button()
    )
    await state.clear()