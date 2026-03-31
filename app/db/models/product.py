"""
Товар в витрине
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from decimal import Decimal

from app.db.models import Base


class ProductStatus(str, Enum):
    """Статусы товара"""
    DRAFT = "draft"  # Черновик
    PENDING = "pending"  # На модерации
    NEEDS_FIX = "needs_fix"  # На доработку
    APPROVED = "approved"  # Одобрен (видим в поиске)
    REJECTED = "rejected"  # Отклонен


class Product(Base):
    """Товар в витрине"""
    __tablename__ = "products"
    
    # Основное
    id = Column(Integer, primary_key=True)
    showcase_id = Column(Integer, ForeignKey("showcases.id", ondelete="CASCADE"), nullable=False, index=True)
    product_name_id = Column(Integer, ForeignKey("product_names.id"), nullable=False)
    
    # Детали товара
    description = Column(Text, nullable=True)
    price_per_kg = Column(Float, nullable=False)  # Цена за килограмм (в валюте витрины)
    quantity_in_stock = Column(Float, nullable=False)  # Текущее количество в наличии (кг)
    
    # Фото
    image_file = Column(String(512), nullable=True)
    
    # Статус
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT, nullable=False)
    
    # Тип торговли
    is_wholesale = Column(Boolean, default=False)  # Опт
    is_retail = Column(Boolean, default=True)  # Розница
    
    # Комментарий модератора (если на доработку или отклонено)
    moderator_comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    showcase = relationship("Showcase", back_populates="products")
    product_name = relationship("ProductName")
    
    def __repr__(self):
        return f"<Product {self.id} ({self.product_name_id})>"