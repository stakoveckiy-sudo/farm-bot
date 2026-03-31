"""
Управление справочником товаров - админ
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


class ProductForms(StatesGroup):
    """FSM для товаров"""
    waiting_for_name = State()
    waiting_for_description = State()


@router.callback_query(F.data == "admin_dict_products", IsAdmin())
async def list_product_names(callback: CallbackQuery, session: AsyncSession):
    """Список наименований товаров"""
    dict_repo = DictionaryRepository(session)
    products = await dict_repo.get_all_product_names()
    
    if not products:
        text = "📋 <b>Наименования товаров</b>\n\nЗаписей нет."
    else:
        text = "📋 <b>Наименования товаров</b>\n\n"
        for i, product in enumerate(products, 1):
            text += f"{i}. {product.name}\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_dict_add_product")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_dict_add_product", IsAdmin())
async def add_product_name(callback: CallbackQuery, state: FSMContext):
    """Добавить наименование товара"""
    await callback.message.edit_text(
        "📝 Введите наименование товара (например: Картофель):",
        reply_markup=get_cancel_button()
    )
    await state.set_state(ProductForms.waiting_for_name)
    await callback.answer()


@router.message(ProductForms.waiting_for_name, IsAdmin())
async def process_product_name(message: Message, state: FSMContext):
    """Обработка названия товара"""
    await state.update_data(product_name=message.text)
    await state.set_state(ProductForms.waiting_for_description)
    await message.answer(
        "📝 Введите описание товара (опционально) или напишите 'Пропустить':",
        reply_markup=get_cancel_button()
    )


@router.message(ProductForms.waiting_for_description, IsAdmin())
async def process_product_description(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка описания товара"""
    data = await state.get_data()
    
    description = None if message.text.lower() in ["пропустить", "skip"] else message.text
    
    dict_repo = DictionaryRepository(session)
    product = await dict_repo.create_product_name(
        name=data['product_name'],
        description=description
    )
    
    logger.info(f"Product name created: {product.id}")
    
    await message.answer(
        f"✅ <b>Товар добавлен!</b>\n\n{product.name}",
        reply_markup=get_cancel_button()
    )
    await state.clear()