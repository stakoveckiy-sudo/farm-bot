"""
Подписка продавца (FREE/PRO)
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.db.models import Base


class SubscriptionPlan(str, Enum):
    """Тип подписки"""
    FREE = "free"
    PRO = "pro"


class Subscription(Base):
    """Подписка продавца"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    seller_profile_id = Column(Integer, ForeignKey("seller_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # План
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    
    # Дата окончания (NULL если бесплатный или бесконечный)
    expires_at = Column(DateTime, nullable=True)
    
    # Статус активности
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    seller_profile = relationship("SellerProfile", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription {self.seller_profile_id} ({self.plan})>"