"""
Импорт всех моделей
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.db.models.user import User
from app.db.models.seller_profile import SellerProfile
from app.db.models.showcase import Showcase
from app.db.models.product import Product
from app.db.models.dict_geo import Country, Region, City
from app.db.models.dict_product_name import ProductName
from app.db.models.dict_legal_form import LegalForm
from app.db.models.subscription import Subscription
from app.db.models.payment import Payment

__all__ = [
    "Base",
    "User",
    "SellerProfile",
    "Showcase",
    "Product",
    "Country",
    "Region",
    "City",
    "ProductName",
    "LegalForm",
    "Subscription",
    "Payment",
]