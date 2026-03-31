"""
Обработчики товаров продавца
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.fsm.product_create import ProductCreateForm
from app.bot.keyboards.seller import get_products_menu, get_product_actions
from app.bot.keyboards.common import get_cancel_button, get_yes_no
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.db.repositories.showcase import ShowcaseRepository
from app.db.repositories.product import ProductRepository
from app.db.repositories.dictionaries import DictionaryRepository
from app.core.settings.config import Config

router = Router()


@router.callback_query(F.data == "seller_products")
async def list_products(callback: CallbackQuery, session: AsyncSession):
    """Список товаров продавца"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    showcase_repo = ShowcaseRepository(session)
    product_repo = ProductRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller:
        await callback.answer("❌ Профиль продавца не найден", show_alert=True)
        return
    
    showcases = await showcase_repo.get_by_seller(seller.id)
    
    if not showcases:
        text = "❌ У вас нет витрин. Создайте витрину первым делом!"
        await callback.message.edit_text(text, reply_markup=get_cancel_button())
        return
    
    # Считаем товары
    total_products = 0
    for showcase in showcases:
        total_products += await product_repo.count_by_showcase(showcase.id)
    
    # Определяем лимит
    from app.db.models.subscription import SubscriptionPlan
    subscriptions = seller.subscriptions
    plan = subscriptions[0].plan if subscriptions else SubscriptionPlan.FREE
    
    limit = Config.PRICING.free_products if plan == SubscriptionPlan.FREE else (Config.PRICING.pro_products_per_showcase * Config.PRICING.pro_showcases)
    
    text = f"📦 <b>Ваши товары</b>\n\nТовары: {total_products}/{limit}\n\nВыберите витрину:"
    
    keyboard_buttons = []
    for showcase in showcases:
        keyboard_buttons.append([
            F"showcase_products:{showcase.id}"
        ])
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🏪 {showcase.name}", callback_data=f"showcase_products:{showcase.id}")]
        for showcase in showcases
    ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="seller_menu")
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("showcase_products:"))
async def list_showcase_products(callback: CallbackQuery, session: AsyncSession):
    """Товары конкретной витрины"""
    showcase_id = int(callback.data.split(":")[1])
    
    showcase_repo = ShowcaseRepository(session)
    product_repo = ProductRepository(session)
    
    showcase = await showcase_repo.get_by_id(showcase_id)
    if not showcase:
        await callback.answer("❌ Витрина не найдена", show_alert=True)
        return
    
    products = await product_repo.get_by_showcase(showcase_id)
    
    if not products:
        text = f"🏪 <b>{showcase.name}</b>\n\nТоваров нет. Добавьте первый товар!"
    else:
        text = f"🏪 <b>{showcase.name}</b>\n\n<b>Товары:</b>\n\n"
        for i, product in enumerate(products, 1):
            status = product.status.value if hasattr(product.status, 'value') else str(product.status)
            text += f"{i}. {product.product_name.name}\n   Цена: {product.price_per_kg}/кг\n   Статус: {status}\n\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data=f"product_create:{showcase_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="seller_products")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product_create:"))
async def start_product_creation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Начало добавления товара"""
    showcase_id = int(callback.data.split(":")[1])
    
    # Проверяем, что витрина существует
    showcase_repo = ShowcaseRepository(session)
    showcase = await showcase_repo.get_by_id(showcase_id)
    
    if not showcase:
        await callback.answer("❌ Витрина не найдена", show_alert=True)
        return
    
    # Сохраняем showcase_id в FSM
    await state.update_data(showcase_id=showcase_id)
    
    # Переходим к выбору наименования товара
    dict_repo = DictionaryRepository(session)
    product_names = await dict_repo.get_all_product_names()
    
    if not product_names:
        await callback.answer("❌ Справочник товаров пуст. Обратитесь в поддержку.", show_alert=True)
        return
    
    text = "📋 <b>Выберите наименование товара:</b>\n\n"
    for i, pn in enumerate(product_names, 1):
        text += f"{i}. {pn.name}\n"
    
    # Создаём кнопки для выбора
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=pn.name, callback_data=f"product_name:{pn.id}")]
        for pn in product_names[:10]  # Максимум 10 кнопок
    ] + [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await state.set_state(ProductCreateForm.waiting_for_product_name)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ProductCreateForm.waiting_for_product_name, F.data.startswith("product_name:"))
async def select_product_name(callback: CallbackQuery, state: FSMContext):
    """Выбор наименования товара"""
    product_name_id = int(callback.data.split(":")[1])
    
    await state.update_data(product_name_id=product_name_id)
    
    # Переходим к цене
    await state.set_state(ProductCreateForm.waiting_for_price)
    await callback.message.edit_text(
        "💰 <b>Цена за кг</b>\n\nВведите цену (например: 150.50):",
        reply_markup=get_cancel_button()
    )
    await callback.answer()


@router.message(ProductCreateForm.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext):
    """Цена товара"""
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer("❌ Неверная цена. Введите число (например: 150.50)")
        return
    
    await state.update_data(price_per_kg=price)
    
    # Переходим к количеству
    await state.set_state(ProductCreateForm.waiting_for_quantity)
    await message.answer(
        "📊 <b>Количество в наличии (кг)</b>\n\nВведите количество:",
        reply_markup=get_cancel_button()
    )


@router.message(ProductCreateForm.waiting_for_quantity)
async def process_product_quantity(message: Message, state: FSMContext):
    """Количество товара"""
    try:
        quantity = float(message.text.replace(",", "."))
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer("❌ Неверное количество. Введите число (например: 100)")
        return
    
    await state.update_data(quantity_in_stock=quantity)
    
    # Переходим к фото
    await state.set_state(ProductCreateForm.waiting_for_image)
    await message.answer(
        "📸 <b>Фото товара</b>\n\nЗагрузите фото товара:",
        reply_markup=get_cancel_button()
    )


@router.message(ProductCreateForm.waiting_for_image, F.photo)
async def process_product_image(message: Message, state: FSMContext):
    """Фото товара"""
    photo = message.photo[-1]
    
    # Проверяем размер
    if photo.file_size and photo.file_size > Config.STORAGE.max_file_size:
        await message.answer("❌ Файл слишком большой. Максимум 25 МБ.")
        return
    
    await state.update_data(image_file_id=photo.file_id)
    
    # Переходим к описанию
    await state.set_state(ProductCreateForm.waiting_for_description)
    await message.answer(
        "📝 <b>Описание товара (опционально)</b>\n\nВведите описание или напишите 'Пропустить':",
        reply_markup=get_cancel_button()
    )


@router.message(ProductCreateForm.waiting_for_image)
async def process_product_image_invalid(message: Message):
    """Неверный формат для фото"""
    await message.answer("❌ Загружайте только изображения")


@router.message(ProductCreateForm.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext):
    """Описание товара"""
    if message.text.lower() in ["пропустить", "skip", "-"]:
        await state.update_data(description=None)
    else:
        await state.update_data(description=message.text)
    
    # Переходим к подтверждению
    await state.set_state(ProductCreateForm.waiting_for_confirmation)
    
    data = await state.get_data()
    confirm_text = f"""
✅ <b>Проверка данных товара</b>

<b>Цена:</b> {data.get('price_per_kg')}/кг
<b>Количество:</b> {data.get('quantity_in_stock')} кг

Все верно?
"""
    
    await message.answer(confirm_text, reply_markup=get_yes_no())


@router.callback_query(ProductCreateForm.waiting_for_confirmation, F.data == "yes")
async def confirm_product(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение создания товара"""
    data = await state.get_data()
    
    product_repo = ProductRepository(session)
    
    try:
        product = await product_repo.create(
            showcase_id=data.get('showcase_id'),
            product_name_id=data.get('product_name_id'),
            price_per_kg=data.get('price_per_kg'),
            quantity_in_stock=data.get('quantity_in_stock'),
            image_file=data.get('image_file_id'),
            description=data.get('description'),
        )
        
        logger.info(f"Product created: {product.id}")
        
        await callback.message.edit_text(
            "✅ <b>Товар добавлен!</b>\n\nТовар отправлен на модерацию. Обычно это занимает несколько часов.",
            reply_markup=get_cancel_button()
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        await callback.message.edit_text("❌ Ошибка при добавлении товара", reply_markup=get_cancel_button())
    
    await callback.answer()


@router.callback_query(ProductCreateForm.waiting_for_confirmation, F.data == "no")
async def reject_product_confirmation(callback: CallbackQuery, state: FSMContext):
    """Отмена, возврат к редактированию"""
    await callback.message.edit_text(
        "💰 <b>Цена за кг</b>\n\nВведите цену (например: 150.50):",
        reply_markup=get_cancel_button()
    )
    await state.set_state(ProductCreateForm.waiting_for_price)
    await callback.answer()