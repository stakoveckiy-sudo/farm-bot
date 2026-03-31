"""
Главный router для всех обработчиков
"""
from aiogram import Router

# Импортируем роутеры
from app.bot.handlers.start import router as start_router
from app.bot.handlers.seller.menu import router as seller_menu_router
from app.bot.handlers.seller.registration import router as seller_reg_router
from app.bot.handlers.seller.showcases import router as seller_showcase_router
from app.bot.handlers.seller.products import router as seller_product_router
from app.bot.handlers.seller.subscription import router as seller_subscription_router
from app.bot.handlers.buyer.menu import router as buyer_menu_router
from app.bot.handlers.buyer.search import router as buyer_search_router
from app.bot.handlers.admin.menu import router as admin_menu_router
from app.bot.handlers.admin.moderation_sellers import router as admin_sellers_router
from app.bot.handlers.admin.moderation_products import router as admin_products_router
from app.bot.handlers.admin.dictionaries_geo import router as admin_geo_router
from app.bot.handlers.admin.dictionaries_products import router as admin_products_dict_router
from app.bot.handlers.admin.dictionaries_legal_forms import router as admin_legal_forms_router
from app.bot.handlers.admin.payment_requisites import router as admin_requisites_router
from app.bot.handlers.admin.broadcast import router as admin_broadcast_router
from app.bot.handlers.admin.settings import router as admin_settings_router


def get_main_router() -> Router:
    """Создаём главный router и регистрируем все обработчики"""
    
    main_router = Router()
    
    # Регистрируем все роутеры
    main_router.include_router(start_router)
    main_router.include_router(seller_menu_router)
    main_router.include_router(seller_reg_router)
    main_router.include_router(seller_showcase_router)
    main_router.include_router(seller_product_router)
    main_router.include_router(seller_subscription_router)
    main_router.include_router(buyer_menu_router)
    main_router.include_router(buyer_search_router)
    main_router.include_router(admin_menu_router)
    main_router.include_router(admin_sellers_router)
    main_router.include_router(admin_products_router)
    main_router.include_router(admin_geo_router)
    main_router.include_router(admin_products_dict_router)
    main_router.include_router(admin_legal_forms_router)
    main_router.include_router(admin_requisites_router)
    main_router.include_router(admin_broadcast_router)
    main_router.include_router(admin_settings_router)
    
    return main_router