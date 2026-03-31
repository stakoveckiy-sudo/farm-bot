"""
Обработчики подписки и оплаты
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from datetime import datetime, timedelta

from app.bot.keyboards.seller import get_subscription_menu, get_payment_menu
from app.bot.keyboards.common import get_cancel_button, get_yes_no
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.db.models.subscription import SubscriptionPlan, Subscription
from app.db.models.payment import Payment, PaymentType, PaymentStatus

router = Router()


@router.callback_query(F.data == "seller_subscription")
async def subscription_menu(callback: CallbackQuery, session: AsyncSession):
    """Меню подписки"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    if not seller or not seller.subscriptions:
        await callback.answer("❌ Подписка не найдена", show_alert=True)
        return
    
    subscription = seller.subscriptions[0]
    
    expires_text = ""
    if subscription.expires_at:
        expires_text = f"Действует до: {subscription.expires_at.strftime('%d.%m.%Y')}"
    
    text = f"""
💳 <b>Подписка</b>

<b>Текущий план:</b> {subscription.plan.value}
{expires_text}

<b>Лимиты:</b>
• Витрины: {'неограниченно' if subscription.plan == SubscriptionPlan.PRO else '1'}
• Товары: {'неограниченно' if subscription.plan == SubscriptionPlan.PRO else '5'}
"""
    
    keyboard = get_subscription_menu(subscription.plan.value, expires_text)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "subscription_upgrade")
async def upgrade_subscription(callback: CallbackQuery, session: AsyncSession):
    """Обновление подписки на PRO"""
    from app.core.settings.config import Config
    
    text = f"""
⬆️ <b>Перейти на PRO</b>

<b>PRO включает:</b>
• до 5 витрин
• до 100 товаров в каждой витрине
• поднятие в топ на неделю

<b>Цена:</b>
• EUR: €{Config.PRICING.pro_price['eur']}
• RUB: ₽{Config.PRICING.pro_price['rub']}
• BYN: Br{Config.PRICING.pro_price['byn']}

<b>Период:</b> 30 дней

Хотите оплатить?
"""
    
    await callback.message.edit_text(text, reply_markup=get_yes_no())
    await callback.answer()


@router.callback_query(F.data == "yes", F.message.text.contains("PRO включает"))
async def confirm_pro_upgrade(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение обновления PRO"""
    user_repo = UserRepository(session)
    seller_repo = SellerRepository(session)
    
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    seller = await seller_repo.get_by_user_id(user.id)
    
    # Создаём запись платежа
    from app.core.settings.config import Config
    
    payment = Payment(
        seller_profile_id=seller.id,
        payment_type=PaymentType.PRO_SUBSCRIPTION,
        amount=Config.PRICING.pro_price['eur'],
        currency="EUR",
        status=PaymentStatus.PENDING,
    )
    
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    
    logger.info(f"Payment created: {payment.id}")
    
    # Показываем меню оплаты
    await callback.message.edit_text(
        f"💳 <b>Оплата #{payment.id}</b>\n\n"
        f"Сумма: €{Config.PRICING.pro_price['eur']} (или эквивалент в другой валюте)\n\n"
        f"Получите реквизиты и отправьте чек.",
        reply_markup=get_payment_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "payment_get_requisites")
async def get_payment_requisites(callback: CallbackQuery, session: AsyncSession):
    """Получить реквизиты для оплаты"""
    # TODO: Здесь должны быть реквизиты из БД
    
    requisites_text = """
💳 <b>Реквизиты для оплаты</b>

<b>Для оплаты через Яндекс.Касса:</b>
https://yandex.ru/kassa

<b>Для прямого перевода:</b>
Счёт: XXXXXXXXXXXX
ИНН: XXXXXX
КПП: XXXXXX

<b>ВНИМАНИЕ!</b>
При переводе укажите номер платежа в описании платежа.

После оплаты загрузите чек для подтверждения.
"""
    
    await callback.message.edit_text(requisites_text, reply_markup=get_payment_menu())
    await callback.answer()


@router.callback_query(F.data == "payment_upload_receipt")
async def upload_receipt(callback: CallbackQuery, state: FSMContext):
    """Загрузить чек оплаты"""
    await callback.message.edit_text(
        "📸 <b>Загрузите чек оплаты</b>\n\nОтправьте фото или документ с подтверждением платежа:",
        reply_markup=get_cancel_button()
    )
    # TODO: FSM для загрузки чека
    await callback.answer()


@router.callback_query(F.data == "subscription_boost")
async def boost_showcase(callback: CallbackQuery, session: AsyncSession):
    """Поднять витрину в топ"""
    from app.core.settings.config import Config
    
    text = f"""
📈 <b>Поднять в топ на неделю</b>

Ваша витрина будет показываться первой в поиске на неделю.

<b>Цена:</b>
• EUR: €{Config.PRICING.top_boost_price['eur']}
• RUB: ₽{Config.PRICING.top_boost_price['rub']}
• BYN: Br{Config.PRICING.top_boost_price['byn']}

<b>Период:</b> 7 дней

Хотите оплатить?
"""
    
    await callback.message.edit_text(text, reply_markup=get_yes_no())
    await callback.answer()