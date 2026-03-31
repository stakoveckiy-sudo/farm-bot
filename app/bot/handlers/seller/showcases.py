"""
Обработчики витрин
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.fsm.showcase_create import ShowcaseCreateForm
from app.bot.keyboards.seller import get_showcases_menu, get_showcase_actions
from app.bot.keyboards.common import get_cancel_button, get_yes_no
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.db.repositories.showcase import ShowcaseRepository
from app.db.repositories.geo import GeoRepository
from app.core.settings.config import Config

router = Router()


@router.callback_query(F.data == "seller_showcases")
async def list_showcases(callback: CallbackQuery, session: AsyncSession):
    """Список витрин продавца"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    showcase_repo = ShowcaseRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        await callback.answer("❌ Профиль продавца не найден", show_alert=True)
        return
    
    showcases = await showcase_repo.get_by_seller(seller.id)
    
    if not showcases:
        text = "🏪 У вас пока нет витрин.\n\nСоздайте первую витрину, чтобы начать продавать!"
    else:
        text = "🏪 <b>Ваши витрины:</b>\n\n"
        for i, showcase in enumerate(showcases, 1):
            text += f"{i}. <b>{showcase.name}</b> ({showcase.country.name if showcase.country else '—'})\n"
    
    # Определяем лимит в зависимости от плана
    from app.db.models.subscription import SubscriptionPlan
    subscriptions = seller.subscriptions
    plan = subscriptions[0].plan if subscriptions else SubscriptionPlan.FREE
    
    limit = Config.PRICING.pro_showcases if plan == SubscriptionPlan.PRO else Config.PRICING.free_showcases
    
    keyboard = get_showcases_menu(len(showcases), limit)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "showcase_create")
async def start_showcase_creation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Начало создания витрины"""
    
    # Проверяем лимит
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    showcase_repo = ShowcaseRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    from app.db.models.subscription import SubscriptionPlan
    subscriptions = seller.subscriptions
    plan = subscriptions[0].plan if subscriptions else SubscriptionPlan.FREE
    limit = Config.PRICING.pro_showcases if plan == SubscriptionPlan.PRO else Config.PRICING.free_showcases
    
    count = await showcase_repo.count_by_seller(seller.id)
    
    if count >= limit:
        await callback.answer(f"❌ Вы достигли лимита витрин ({limit}). Перейдите на PRO для большего количества.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🏪 <b>Создание витрины</b>\n\nВведите название витрины:",
        reply_markup=get_cancel_button()
    )
    await state.set_state(ShowcaseCreateForm.waiting_for_name)
    await callback.answer()


@router.message(ShowcaseCreateForm.waiting_for_name)
async def process_showcase_name(message: Message, state: FSMContext):
    """Название витрины"""
    if not message.text or len(message.text) < 2:
        await message.answer("❌ Название слишком короткое.")
        return
    
    await state.update_data(showcase_name=message.text)
    
    # Переходим к выбору страны
    await state.set_state(ShowcaseCreateForm.waiting_for_country)
    await message.answer(
        "🌍 <b>Выберите страну:</b>\n\nРФ — Россия\nРБ — Беларусь",
        reply_markup=get_cancel_button()
    )


@router.message(ShowcaseCreateForm.waiting_for_country)
async def process_showcase_country(message: Message, state: FSMContext, session: AsyncSession):
    """Страна"""
    code = message.text.upper().strip()
    
    if code not in ["РФ", "РБ"]:
        await message.answer("❌ Выберите РФ или РБ")
        return
    
    geo_repo = GeoRepository(session)
    country = await geo_repo.get_country_by_code("RU" if code == "РФ" else "BY")
    
    if not country:
        await message.answer("❌ Страна не найдена. Обратитесь в поддержку.")
        return
    
    await state.update_data(country_id=country.id)
    
    # Переходим к регионам
    regions = await geo_repo.get_regions_by_country(country.id)
    
    if not regions:
        await message.answer("❌ Регионы не найдены")
        return
    
    text = "🗺️ <b>Выберите регион:</b>\n\n"
    for region in regions:
        text += f"{region.name}\n"
    
    await state.set_state(ShowcaseCreateForm.waiting_for_region)
    await message.answer(text + "\n(Введите название региона)", reply_markup=get_cancel_button())


@router.message(ShowcaseCreateForm.waiting_for_region)
async def process_showcase_region(message: Message, state: FSMContext, session: AsyncSession):
    """Регион"""
    region_name = message.text.strip()
    
    data = await state.get_data()
    geo_repo = GeoRepository(session)
    
    regions = await geo_repo.get_regions_by_country(data['country_id'])
    region = next((r for r in regions if r.name.lower() == region_name.lower()), None)
    
    if not region:
        await message.answer("❌ Регион не найден")
        return
    
    await state.update_data(region_id=region.id)
    
    # Переходим к городам
    cities = await geo_repo.get_cities_by_region(region.id)
    
    text = "🏙️ <b>Выберите город (или пропустите для всей области):</b>\n\n"
    for city in cities:
        text += f"• {city.name}\n"
    
    await state.set_state(ShowcaseCreateForm.waiting_for_city)
    await message.answer(text + "\n(Введите название города или напишите 'Пропустить')", reply_markup=get_cancel_button())


@router.message(ShowcaseCreateForm.waiting_for_city)
async def process_showcase_city(message: Message, state: FSMContext, session: AsyncSession):
    """Город"""
    text = message.text.strip()
    
    if text.lower() in ["пропустить", "skip", "-"]:
        await state.update_data(city_id=None)
    else:
        data = await state.get_data()
        geo_repo = GeoRepository(session)
        
        cities = await geo_repo.get_cities_by_region(data['region_id'])
        city = next((c for c in cities if c.name.lower() == text.lower()), None)
        
        if not city:
            await message.answer("❌ Город не найден")
            return
        
        await state.update_data(city_id=city.id)
    
    # Переходим к типу торговли
    await state.set_state(ShowcaseCreateForm.waiting_for_trading_type)
    await message.answer(
        "🛒 <b>Тип торговли:</b>\n\n• Опт\n• Розница\n• Опт и Розница",
        reply_markup=get_cancel_button()
    )


@router.message(ShowcaseCreateForm.waiting_for_trading_type)
async def process_showcase_trading(message: Message, state: FSMContext):
    """Тип торговли"""
    choice = message.text.strip().lower()
    
    if "опт" in choice and "розница" in choice:
        await state.update_data(is_wholesale=True, is_retail=True)
    elif "опт" in choice:
        await state.update_data(is_wholesale=True, is_retail=False)
    elif "розница" in choice:
        await state.update_data(is_wholesale=False, is_retail=True)
    else:
        await message.answer("❌ Выберите: Опт, Розница или Опт и Розница")
        return
    
    # Переходим к доставке
    await state.set_state(ShowcaseCreateForm.waiting_for_delivery)
    await message.answer(
        "🚚 <b>Вы доставляете товар своим транспортом?</b>\n\nДа / Нет",
        reply_markup=get_yes_no()
    )


@router.callback_query(ShowcaseCreateForm.waiting_for_delivery)
async def process_showcase_delivery(callback: CallbackQuery, state: FSMContext):
    """Доставка"""
    if callback.data == "yes":
        await state.update_data(is_delivery_available=True)
        # Переходим к телефону
        await state.set_state(ShowcaseCreateForm.waiting_for_phone)
        await callback.message.edit_text("📱 Введите телефон витрины:", reply_markup=get_cancel_button())
    else:
        await state.update_data(is_delivery_available=False)
        # Переходим к адресу самовывоза
        await state.set_state(ShowcaseCreateForm.waiting_for_pickup_address)
        await callback.message.edit_text("📍 Введите адрес самовывоза:", reply_markup=get_cancel_button())
    
    await callback.answer()


@router.message(ShowcaseCreateForm.waiting_for_pickup_address)
async def process_showcase_pickup(message: Message, state: FSMContext):
    """Адрес самовывоза"""
    if not message.text:
        await message.answer("❌ Адрес не может быть пустым")
        return
    
    await state.update_data(pickup_address=message.text)
    
    # Переходим к телефону
    await state.set_state(ShowcaseCreateForm.waiting_for_phone)
    await message.answer("📱 Введите телефон витрины:", reply_markup=get_cancel_button())


@router.message(ShowcaseCreateForm.waiting_for_phone)
async def process_showcase_phone(message: Message, state: FSMContext):
    """Телефон витрины"""
    phone = message.text.strip()
    
    if not phone or len(phone) < 10:
        await message.answer("❌ Неверный номер телефона")
        return
    
    await state.update_data(phone=phone)
    
    # Переходим к логотипу (опционально)
    await state.set_state(ShowcaseCreateForm.waiting_for_logo)
    await message.answer("🖼️ <b>Логотип витрины (опционально)</b>\n\nЗагрузите фото или напишите 'Пропустить':")


@router.message(ShowcaseCreateForm.waiting_for_logo, F.photo)
async def process_showcase_logo(message: Message, state: FSMContext):
    """Логотип"""
    photo = message.photo[-1]
    await state.update_data(logo_file_id=photo.file_id)
    
    # Переходим к подтверждению
    await state.set_state(ShowcaseCreateForm.waiting_for_confirmation)
    
    data = await state.get_data()
    confirm_text = f"""
✅ <b>Проверка данных витрины</b>

<b>Название:</b> {data.get('showcase_name')}
<b>Тип торговли:</b> {"Опт и Розница" if data.get('is_wholesale') and data.get('is_retail') else ("Опт" if data.get('is_wholesale') else "Розница")}
<b>Доставка:</b> {"Да" if data.get('is_delivery_available') else "Нет"}
<b>Телефон:</b> {data.get('phone')}

Все верно?
"""
    
    await message.answer(confirm_text, reply_markup=get_yes_no())


@router.message(ShowcaseCreateForm.waiting_for_logo)
async def process_showcase_logo_skip(message: Message, state: FSMContext):
    """Пропуск логотипа"""
    if message.text.lower() in ["пропустить", "skip", "-"]:
        await state.update_data(logo_file_id=None)
        
        # Переходим к подтверждению
        await state.set_state(ShowcaseCreateForm.waiting_for_confirmation)
        
        data = await state.get_data()
        confirm_text = f"""
✅ <b>Проверка данных витрины</b>

<b>Название:</b> {data.get('showcase_name')}
<b>Тип торговли:</b> {"Опт и Розница" if data.get('is_wholesale') and data.get('is_retail') else ("Опт" if data.get('is_wholesale') else "Розница")}
<b>Доставка:</b> {"Да" if data.get('is_delivery_available') else "Нет"}
<b>Телефон:</b> {data.get('phone')}

Все верно?
"""
        
        await message.answer(confirm_text, reply_markup=get_yes_no())
    else:
        await message.answer("❌ Загрузите фото или напишите 'Пропустить'")


@router.callback_query(ShowcaseCreateForm.waiting_for_confirmation, F.data == "yes")
async def confirm_showcase(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение создания витрины"""
    data = await state.get_data()
    
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    showcase_repo = ShowcaseRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    try:
        showcase = await showcase_repo.create(
            seller_profile_id=seller.id,
            name=data.get('showcase_name'),
            country_id=data.get('country_id'),
            region_id=data.get('region_id'),
            city_id=data.get('city_id'),
            is_wholesale=data.get('is_wholesale', False),
            is_retail=data.get('is_retail', True),
            is_delivery_available=data.get('is_delivery_available', False),
            pickup_address=data.get('pickup_address'),
            phone=data.get('phone'),
            logo_file=data.get('logo_file_id'),
        )
        
        logger.info(f"Showcase created: {showcase.id}")
        
        await callback.message.edit_text(
            f"✅ <b>Витрина создана!</b>\n\n{showcase.name}\n\nТеперь вы можете добавлять товары.",
            reply_markup=get_yes_no()  # Кнопка "Добавить товар"
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error creating showcase: {e}")
        await callback.message.edit_text("❌ Ошибка при создании витрины", reply_markup=get_cancel_button())
    
    await callback.answer()


@router.callback_query(ShowcaseCreateForm.waiting_for_confirmation, F.data == "no")
async def reject_showcase_confirmation(callback: CallbackQuery, state: FSMContext):
    """Отмена, возврат к редактированию"""
    await callback.message.edit_text("🏪 Введите название витрины:", reply_markup=get_cancel_button())
    await state.set_state(ShowcaseCreateForm.waiting_for_name)
    await callback.answer()