"""
История платежей
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Float, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.db.models import Base


class PaymentType(str, Enum):
    """Тип платежа"""
    PRO_SUBSCRIPTION = "pro_subscription"  # Подписка PRO
    TOP_BOOST = "top_boost"  # Поднятие в топ на неделю


class PaymentStatus(str, Enum):
    """Статус платежа"""
    PENDING = "pending"  # Ожидание оплаты
    AWAITING_CHECK = "awaiting_check"  # Чек загружен, ожидает проверки админа
    APPROVED = "approved"  # Одобрен, доступ активирован
    REJECTED = "rejected"  # Отклонен


class Payment(Base):
    """Платёж"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    seller_profile_id = Column(Integer, ForeignKey("seller_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Тип платежа
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    
    # Сумма и валюта
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # EUR, RUB, BYN
    
    # Статус
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Реквизиты (какие данные дали продавцу)
    requisites = Column(Text, nullable=True)  # JSON: {card, account, link, etc}
    
    # Чек от продавца
    receipt_file = Column(String(512), nullable=True)  # Фото чека
    receipt_uploaded_at = Column(DateTime, nullable=True)
    
    # Комментарий админа (если отклонено)
    moderator_comment = Column(Text, nullable=True)
    
    # Для активации подписки
    subscription_expires_at = Column(DateTime, nullable=True)  # Когда заканчивается доступ
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Payment {self.id} ({self.status})>"