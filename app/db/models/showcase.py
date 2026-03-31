"""
Витрина продавца
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.models import Base


class Showcase(Base):
    """Витрина продавца (может быть несколько)"""
    __tablename__ = "showcases"
    
    # Основное
    id = Column(Integer, primary_key=True)
    seller_profile_id = Column(Integer, ForeignKey("seller_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Данные витрины
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Логотип
    logo_file = Column(String(512), nullable=True)
    
    # География
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)  # Может быть NULL если "по всей области"
    
    # Торговля
    is_wholesale = Column(Boolean, default=False)  # Опт
    is_retail = Column(Boolean, default=True)  # Розница
    
    # Доставка
    is_delivery_available = Column(Boolean, default=False)  # Доставка транспортом
    pickup_address = Column(Text, nullable=True)  # Адрес самовывоза (если доставки нет)
    
    # Контакты витрины
    phone = Column(String(20), nullable=False)
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    seller_profile = relationship("SellerProfile", back_populates="showcases")
    country = relationship("Country")
    region = relationship("Region")
    city = relationship("City")
    products = relationship("Product", back_populates="showcase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Showcase {self.id} ({self.name})>"