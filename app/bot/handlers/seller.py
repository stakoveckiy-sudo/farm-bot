"""
Обработчики для продавцов
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.bot.keyboards.common import get_home_button
from app.db.repositories.seller import SellerRepository

router = Router()


@router.callback_query(F.data == "fill_seller_data")
async def start_seller_registration(callback: CallbackQuery):
    """Начало регистрации продавца"""
    text = """
📝 <b>Регистрация продавца</b>

Пожалуйста, заполните данные вашей компании. Все данные будут проверены модератором.

Начнём с названия компании:
"""
    await callback.message.edit_text(text, reply_markup=get_home_button())
    await callback.answer()


@router.message()
async def handle_seller_registration(message: Message, session: AsyncSession):
    """Обработка данных продавца"""
    # TODO: Добавить логику сохранения данных
    logger.info(f"Seller data received: {message.text}")
    await message.answer("✓ Спасибо! Данные отправлены на проверку.")
