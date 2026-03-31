"""
Географические справочники (страны/регионы/города)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.models import Base


class Country(Base):
    """Страна"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(2), unique=True, nullable=False)  # RU, BY
    currency = Column(String(3), nullable=False)  # RUB, BYN
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    regions = relationship("Region", back_populates="country", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Country {self.code} ({self.name})>"


class Region(Base):
    """Регион/Область"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    country = relationship("Country", back_populates="regions")
    cities = relationship("City", back_populates="region", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Уникальность: одна область в одной стране не может повторяться
        # но разные страны могут иметь области с одинаковыми названиями
    )
    
    def __repr__(self):
        return f"<Region {self.name}>"


class City(Base):
    """Город"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    region = relationship("Region", back_populates="cities")
    
    def __repr__(self):
        return f"<City {self.name}>"