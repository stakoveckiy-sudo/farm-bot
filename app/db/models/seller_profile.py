"""
Профиль продавца
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.db.models import Base


class SellerStatus(str, Enum):
    """Статусы продавца"""
    NONE = "none"  # Ещё не заполнял данные
    PENDING = "pending"  # На модерации
    NEEDS_FIX = "needs_fix"  # На доработку
    APPROVED = "approved"  # Одобрен
    REJECTED = "rejected"  # Отклонен
    BLOCKED = "blocked"  # Заблокирован (например за неоплату)


class SellerProfile(Base):
    """Профиль продавца (юридические данные)"""
    __tablename__ = "seller_profiles"
    
    # Основное
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Статус регистрации
    status = Column(SQLEnum(SellerStatus), default=SellerStatus.NONE, nullable=False)
    
    # Данные компании
    company_name = Column(String(255), nullable=True)
    legal_form_id = Column(Integer, ForeignKey("legal_forms.id"), nullable=True)  # ООО/ИП/ЧП и т.д.
    
    # ФИО владельца
    owner_name = Column(String(255), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    
    # ИНН / УНП (в зависимости от страны)
    inn_unp = Column(String(20), nullable=True, index=True)
    
    # Документы (пути к файлам)
    passport_file = Column(String(512), nullable=True)  # Фото паспорта
    registration_cert_file = Column(String(512), nullable=True)  # Свидетельство о регистрации
    
    # Комментарий модератора (если на доработку или отклонено)
    moderator_comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="seller_profile")
    legal_form = relationship("LegalForm")
    showcases = relationship("Showcase", back_populates="seller_profile", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="seller_profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SellerProfile {self.user_id} ({self.status})>"