"""
Справочник форм юрлица (редактируется админом)
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.models import Base


class LegalForm(Base):
    """Форма юрлица (ООО, ИП, ЧП и т.д.)"""
    __tablename__ = "legal_forms"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # ООО, ИП, ЧП
    code = Column(String(10), unique=True, nullable=False)  # LLC, IP, CP (опционально, для внутреннего использования)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<LegalForm {self.name}>"