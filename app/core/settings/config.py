"""
Конфигурация приложения
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Config:
    """Главная конфигурация"""
    
    # === BOT ===
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BOT_SERVER_HOST = os.getenv("BOT_SERVER_HOST", "0.0.0.0")
    BOT_SERVER_PORT = int(os.getenv("BOT_SERVER_PORT", "8000"))
    
    # === WEBHOOK ===
    class WEBHOOK:
        domain = os.getenv("WEBHOOK_HOST", "localhost")
        path = os.getenv("WEBHOOK_PATH", "/webhook/telegram")
        full_url = f"https://{domain}{path}"
    
    # === DATABASE ===
    class DB:
        url = os.getenv("DATABASE_URL")
        echo = os.getenv("DATABASE_ECHO", "False").lower() == "true"
        pool_size = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    # === REDIS ===
    class REDIS:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        password = os.getenv("REDIS_PASSWORD")
    
    # === STORAGE ===
    class STORAGE:
        root_path = os.getenv("STORAGE_PATH", str(BASE_DIR / "app" / "storage"))
        images_path = os.path.join(root_path, "images")
        max_file_size = int(os.getenv("MAX_FILE_SIZE", "26214400"))  # 25 MB
    
    # === APP ===
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "426602668").split(",")))
    
    # === PRICING ===
    class PRICING:
        free_showcases = 1
        free_products = 5
        pro_showcases = 5
        pro_products_per_showcase = 100
        
        pro_price = {
            "eur": 5.0,
            "rub": 500,
            "byn": 15,
        }
        
        top_boost_price = {
            "eur": 2.0,
            "rub": 200,
            "byn": 6,
        }


# Проверяем обязательные переменные
def validate_config():
    """Валидация конфига"""
    required = ["BOT_TOKEN", "DATABASE_URL"]
    
    if not Config.BOT_TOKEN:
        raise ValueError("Missing BOT_TOKEN in .env")
    if not Config.DB.url:
        raise ValueError("Missing DATABASE_URL in .env")


# Валидируем при импорте
validate_config()
