"""
Поиск товаров для покупателей
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.buyer import get_search_menu
from app.db.repositories.product import ProductRepository
from app.db.repositories.geo import GeoRepository

router = Router()


@router.callback_query(F.data == "search_start")
async def start_search(callback: CallbackQuery, session: AsyncSession):
    """Начало поиска"""
    geo_repo = GeoRepository(session)
    
    countries = await geo_repo.get_all_countries()
    
    if not countries:
        await callback.message.edit_text("❌ Справочник стран пуст")
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = "🌍 <b>Выберите страну:</b>\n\n"
    
    buttons = [
        [InlineKeyboardButton(text=f"{country.name}", callback_data=f"search_country:{country.id}")]
        for country in countries
    ]
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="buyer_search")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("search_country:"))
async def search_by_country(callback: CallbackQuery, session: AsyncSession):
    """Поиск по стране"""
    country_id = int(callback.data.split(":")[1])
    
    geo_repo = GeoRepository(session)
    regions = await geo_repo.get_regions_by_country(country_id)
    
    if not regions:
        await callback.message.edit_text("❌ В этой стране нет регионов")
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = "🗺️ <b>Выберите регион:</b>\n\n"
    
    buttons = [
        [InlineKeyboardButton(text=f"{region.name}", callback_data=f"search_region:{region.id}")]
        for region in regions
    ]
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_start")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("search_region:"))
async def search_by_region(callback: CallbackQuery, session: AsyncSession):
    """Поиск по региону"""
    region_id = int(callback.data.split(":")[1])
    
    geo_repo = GeoRepository(session)
    showcase_repo = ShipShowcaseRepository(session)
    
    showcases = await showcase_repo.search(region_id=region_id)
    
    if not showcases:
        await callback.message.edit_text(
            "❌ В этом регионе нет продавцов",
            reply_markup=get_search_menu()
        )
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = "🏪 <b>Найденные витрины:</b>\n\n"
    
    buttons = []
    for showcase in showcases[:20]:  # Максимум 20
        text += f"• {showcase.name} ({showcase.city.name if showcase.city else showcase.region.name})\n"
        buttons.append([InlineKeyboardButton(text=f"📦 {showcase.name}", callback_data=f"showcase_view:{showcase.id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="search_start")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("showcase_view:"))
async def view_showcase(callback: CallbackQuery, session: AsyncSession):
    """Просмотр витрины"""
    showcase_id = int(callback.data.split(":")[1])
    
    showcase_repo = ShowcaseRepository(session)
    product_repo = ProductRepository(session)
    
    showcase = await showcase_repo.get_by_id(showcase_id)
    
    if not showcase:
        await callback.answer("❌ Витрина не найдена", show_alert=True)
        return
    
    products = await product_repo.get_by_showcase(showcase_id)
    
    text = f"""
🏪 <b>{showcase.name}</b>

<b>Место:</b> {showcase.city.name if showcase.city else showcase.region.name}
<b>Телефон:</b> {showcase.phone}
<b>Доставка:</b> {"✅ Да" if showcase.is_delivery_available else "❌ Нет"}
<b>Адрес самовывоза:</b> {showcase.pickup_address or "—"}

<b>Товары:</b> {len(products)}
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    if products:
        buttons.append([InlineKeyboardButton(text="📦 Товары", callback_data=f"showcase_products:{showcase_id}")])
    
    buttons.extend([
        [InlineKeyboardButton(text="☎️ Позвонить", callback_data=f"contact_call:{showcase.phone}")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data=f"contact_telegram:{showcase.seller_profile.user.username or '?'}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="search_start")],
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("showcase_products:"))
async def view_showcase_products(callback: CallbackQuery, session: AsyncSession):
    """Товары витрины"""
    showcase_id = int(callback.data.split(":")[1])
    
    product_repo = ProductRepository(session)
    showcase_repo = ShowcaseRepository(session)
    
    showcase = await showcase_repo.get_by_id(showcase_id)
    products = await product_repo.get_by_showcase(showcase_id)
    
    # Фильтруем только одобренные товары
    from app.db.models.product import ProductStatus
    approved_products = [p for p in products if p.status == ProductStatus.APPROVED]
    
    if not approved_products:
        await callback.message.edit_text("❌ В этой витрине нет товаров")
        await callback.answer()
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = f"📦 <b>Товары витрины '{showcase.name}'</b>\n\n"
    
    buttons = []
    for product in approved_products[:20]:
        text += f"• {product.product_name.name}: {product.price_per_kg}/кг (наличие: {product.quantity_in_stock} кг)\n"
        buttons.append([InlineKeyboardButton(text=f"📦 {product.product_name.name}", callback_data=f"product_view:{product.id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"showcase_view:{showcase_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product_view:"))
async def view_product(callback: CallbackQuery, session: AsyncSession):
    """Просмотр товара"""
    product_id = int(callback.data.split(":")[1])
    
    product_repo = ProductRepository(session)
    product = await product_repo.get_by_id(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    showcase = product.showcase
    seller = showcase.seller_profile
    user = seller.user
    
    text = f"""
📦 <b>{product.product_name.name}</b>

<b>Цена:</b> {product.price_per_kg} {showcase.country.currency}/кг
<b>Наличие:</b> {product.quantity_in_stock} кг
<b>Описание:</b> {product.description or "—"}

<b>Продавец:</b> {showcase.name}
<b>Телефон:</b> {showcase.phone}
<b>Место:</b> {showcase.city.name if showcase.city else showcase.region.name}
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="☎️ Позвонить", callback_data=f"contact_call:{showcase.phone}")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data=f"contact_tg:{user.username or '?'}")],
        [InlineKeyboardButton(text="🏪 Витрина", callback_data=f"showcase_view:{showcase.id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"showcase_products:{showcase.id}")],
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("contact_call:"))
async def contact_call(callback: CallbackQuery):
    """Контакт: позвонить"""
    phone = callback.data.split(":")[1]
    await callback.answer(f"Номер: {phone}", show_alert=True)


@router.callback_query(F.data.startswith("contact_telegram:"))
async def contact_telegram(callback: CallbackQuery):
    """Контакт: Telegram"""
    username = callback.data.split(":")[1]
    await callback.answer(f"Напишите: @{username}", show_alert=True)