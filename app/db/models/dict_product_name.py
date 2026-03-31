"""
Справочник наименований товаров (редактируется админом)
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.models import Base


class ProductName(Base):
    """Наименование товара (справочник)"""
    __tablename__ = "product_names"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ProductName {self.name}>"