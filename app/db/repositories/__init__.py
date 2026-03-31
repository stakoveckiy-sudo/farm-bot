"""
Repositories для работы с БД
"""
from app.db.repositories.user import UserRepository
from app.db.repositories.seller import SellerRepository
from app.db.repositories.showcase import ShowcaseRepository
from app.db.repositories.product import ProductRepository
from app.db.repositories.geo import GeoRepository
from app.db.repositories.dictionaries import DictionaryRepository

__all__ = [
    "UserRepository",
    "SellerRepository",
    "ShowcaseRepository",
    "ProductRepository",
    "GeoRepository",
    "DictionaryRepository",
]