"""
Управление географией (страны, регионы, города) - админ
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.filters.is_admin import IsAdmin
from app.bot.keyboards.admin import get_geo_menu
from app.bot.keyboards.common import get_cancel_button, get_yes_no
from app.db.repositories.geo import GeoRepository

router = Router()


class GeoForms(StatesGroup):
    """FSM для управления географией"""
    waiting_for_country_name = State()
    waiting_for_country_code = State()
    waiting_for_country_currency = State()
    waiting_for_region_name = State()
    waiting_for_city_name = State()


@router.callback_query(F.data == "admin_geo", IsAdmin())
async def geo_menu(callback: CallbackQuery):
    """Меню географии"""
    await callback.message.edit_text(
        "🗺️ <b>Управление географией</b>\n\nВыберите действие:",
        reply_markup=get_geo_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_geo_countries", IsAdmin())
async def list_countries(callback: CallbackQuery, session: AsyncSession):
    """Список стран"""
    geo_repo = GeoRepository(session)
    countries = await geo_repo.get_all_countries()
    
    if not countries:
        text = "🌍 <b>Страны</b>\n\nЗаписей нет."
    else:
        text = "🌍 <b>Страны</b>\n\n"
        for country in countries:
            text += f"• {country.name} ({country.code}) - {country.currency}\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить страну", callback_data="admin_geo_add_country")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_geo")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_geo_add_country", IsAdmin())
async def add_country(callback: CallbackQuery, state: FSMContext):
    """Добавить страну"""
    await callback.message.edit_text(
        "🌍 Введите название страны (например: Россия):",
        reply_markup=get_cancel_button()
    )
    await state.set_state(GeoForms.waiting_for_country_name)
    await callback.answer()


@router.message(GeoForms.waiting_for_country_name, IsAdmin())
async def process_country_name(message: Message, state: FSMContext):
    """Обработка названия страны"""
    await state.update_data(country_name=message.text)
    await state.set_state(GeoForms.waiting_for_country_code)
    await message.answer("📌 Введите код страны (2 буквы, например: RU):")


@router.message(GeoForms.waiting_for_country_code, IsAdmin())
async def process_country_code(message: Message, state: FSMContext):
    """Обработка кода страны"""
    code = message.text.upper().strip()
    
    if len(code) != 2:
        await message.answer("❌ Код должен быть 2 буквы (например: RU)")
        return
    
    await state.update_data(country_code=code)
    await state.set_state(GeoForms.waiting_for_country_currency)
    await message.answer("💱 Введите код валюты (3 буквы, например: RUB):")


@router.message(GeoForms.waiting_for_country_currency, IsAdmin())
async def process_country_currency(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка валюты страны"""
    currency = message.text.upper().strip()
    
    if len(currency) != 3:
        await message.answer("❌ Код валюты должен быть 3 буквы (например: RUB)")
        return
    
    data = await state.get_data()
    
    geo_repo = GeoRepository(session)
    country = await geo_repo.create_country(
        name=data['country_name'],
        code=data['country_code'],
        currency=currency
    )
    
    logger.info(f"Country created: {country.id}")
    
    await message.answer(
        f"✅ <b>Страна добавлена!</b>\n\n{country.name} ({country.code})",
        reply_markup=get_cancel_button()
    )
    await state.clear()


@router.callback_query(F.data == "admin_geo_regions", IsAdmin())
async def list_regions(callback: CallbackQuery, session: AsyncSession):
    """Список регионов"""
    geo_repo = GeoRepository(session)
    countries = await geo_repo.get_all_countries()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = "🗺️ <b>Регионы</b>\n\nВыберите страну:"
    
    buttons = [
        [InlineKeyboardButton(text=f"{country.name}", callback_data=f"admin_geo_regions_list:{country.id}")]
        for country in countries
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_geo")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_geo_regions_list:"), IsAdmin())
async def list_country_regions(callback: CallbackQuery, session: AsyncSession):
    """Список регионов страны"""
    country_id = int(callback.data.split(":")[1])
    
    geo_repo = GeoRepository(session)
    regions = await geo_repo.get_regions_by_country(country_id)
    
    if not regions:
        text = "🗺️ <b>Регионы</b>\n\nЗаписей нет."
    else:
        text = "🗺️ <b>Регионы</b>\n\n"
        for region in regions:
            text += f"• {region.name}\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить регион", callback_data=f"admin_geo_add_region:{country_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_geo_regions")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()