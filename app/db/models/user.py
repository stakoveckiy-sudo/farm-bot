"""
Модель пользователя (может быть продавцом и/или покупателем)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.db.models import Base


class UserRole(str, Enum):
    """Роли пользователя"""
    BUYER = "buyer"
    SELLER = "seller"


class User(Base):
    """Пользователь Telegram бота"""
    __tablename__ = "users"
    
    # Основное
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Роли (может быть обе)
    is_buyer = Column(Boolean, default=False)
    is_seller = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Статусы
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.telegram_id} ({self.first_name})>"