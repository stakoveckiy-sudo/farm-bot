"""
Загрузка и парсинг переменных окружения
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Главная конфигурация приложения"""
    
    # ============== TELEGRAM ==============
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_bot_api_id: int = Field(94575, alias="TELEGRAM_BOT_API_ID")
    telegram_bot_api_hash: str = Field(..., alias="TELEGRAM_BOT_API_HASH")
    
    # ============== ADMIN ==============
    admin_ids_str: str = Field("426602668", alias="ADMIN_IDS")
    
    @property
    def admin_ids(self) -> List[int]:
        """Парсим строку админов в список"""
        return [int(id_.strip()) for id_ in self.admin_ids_str.split(",") if id_.strip()]
    
    # ============== DATABASE ==============
    database_url: str = Field(..., alias="DATABASE_URL")
    database_echo: bool = Field(False, alias="DATABASE_ECHO")
    database_pool_size: int = Field(20, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(20, alias="DATABASE_MAX_OVERFLOW")
    
    # ============== REDIS ==============
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_password: str = Field("", alias="REDIS_PASSWORD")
    
    # ============== WEBHOOK ==============
    webhook_host: str = Field("farm-store.ru", alias="WEBHOOK_HOST")
    webhook_port: int = Field(8080, alias="WEBHOOK_PORT")
    webhook_path: str = Field("/webhook/telegram", alias="WEBHOOK_PATH")
    webhook_secret: str = Field("change_me", alias="WEBHOOK_SECRET")
    
    # ============== BOT SERVER ==============
    bot_server_host: str = Field("127.0.0.1", alias="BOT_SERVER_HOST")
    bot_server_port: int = Field(8080, alias="BOT_SERVER_PORT")
    
    # ============== STORAGE ==============
    storage_path: str = Field("/opt/farm-store/app/storage", alias="STORAGE_PATH")
    images_path: str = Field("/opt/farm-store/app/storage/images", alias="IMAGES_PATH")
    max_image_size: int = Field(25000000, alias="MAX_IMAGE_SIZE")
    
    # ============== CURRENCY ==============
    rub_rate_source: str = Field(
        "https://www.cbr-xml-daily.ru/daily_json.js",
        alias="RUB_RATE_SOURCE"
    )
    byn_rate_source: str = Field(
        "https://www.nbrb.by/api/exrates/rates/840",
        alias="BYN_RATE_SOURCE"
    )
    
    # ============== PRICING ==============
    free_showcases_limit: int = Field(1, alias="FREE_SHOWCASES_LIMIT")
    free_products_limit: int = Field(5, alias="FREE_PRODUCTS_LIMIT")
    
    pro_showcases_limit: int = Field(5, alias="PRO_SHOWCASES_LIMIT")
    pro_products_per_showcase: int = Field(100, alias="PRO_PRODUCTS_PER_SHOWCASE")
    pro_price_eur: float = Field(30.0, alias="PRO_PRICE_EUR")
    pro_price_rub: float = Field(2500.0, alias="PRO_PRICE_RUB")
    pro_price_byn: float = Field(75.0, alias="PRO_PRICE_BYN")
    
    top_boost_price_eur: float = Field(2.0, alias="TOP_BOOST_PRICE_EUR")
    top_boost_price_rub: float = Field(165.0, alias="TOP_BOOST_PRICE_RUB")
    top_boost_price_byn: float = Field(5.0, alias="TOP_BOOST_PRICE_BYN")
    
    # ============== NOTIFICATIONS ==============
    subscription_reminder_days_str: str = Field("3,2,1", alias="SUBSCRIPTION_REMINDER_DAYS")
    subscription_reminder_hour: int = Field(12, alias="SUBSCRIPTION_REMINDER_HOUR")
    
    @property
    def subscription_reminder_days(self) -> List[int]:
        """Парсим дни напоминания"""
        return [int(d.strip()) for d in self.subscription_reminder_days_str.split(",")]
    
    # ============== FEATURES ==============
    passport_check_enabled: bool = Field(True, alias="PASSPORT_CHECK_ENABLED")
    duplicate_check_enabled: bool = Field(True, alias="DUPLICATE_CHECK_ENABLED")
    auto_moderate_products: bool = Field(False, alias="AUTO_MODERATE_PRODUCTS")
    
    # ============== DEBUG ==============
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный инстанс
settings = Settings()