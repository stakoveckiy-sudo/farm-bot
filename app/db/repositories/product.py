"""
Repository для работы с товарами
"""
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.db.models.product import Product, ProductStatus
from loguru import logger


class ProductRepository:
    """CRUD операции для товаров"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        showcase_id: int,
        product_name_id: int,
        price_per_kg: float,
        quantity_in_stock: float,
        is_wholesale: bool = False,
        is_retail: bool = True,
        image_file: str | None = None,
        description: str | None = None,
    ) -> Product:
        """Создать товар"""
        product = Product(
            showcase_id=showcase_id,
            product_name_id=product_name_id,
            price_per_kg=price_per_kg,
            quantity_in_stock=quantity_in_stock,
            is_wholesale=is_wholesale,
            is_retail=is_retail,
            image_file=image_file,
            description=description,
            status=ProductStatus.PENDING,  # На модерацию
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        logger.info(f"Создан товар: {product.id} (витрина={showcase_id})")
        return product
    
    async def get_by_id(self, product_id: int) -> Product | None:
        """Получить товар по ID"""
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_showcase(self, showcase_id: int) -> list[Product]:
        """Получить все товары витрины"""
        stmt = select(Product).where(Product.showcase_id == showcase_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_by_showcase(self, showcase_id: int) -> int:
        """Подсчитать товары в витрине"""
        stmt = select(Product).where(Product.showcase_id == showcase_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
    
    async def get_pending_products(self) -> list[Product]:
        """Получить товары на модерации"""
        stmt = select(Product).where(Product.status == ProductStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def approve_product(self, product_id: int) -> Product:
        """Одобрить товар"""
        product = await self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_id}")
        
        product.status = ProductStatus.APPROVED
        product.approved_at = datetime.utcnow()
        product.moderator_comment = None
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        logger.info(f"Товар одобрен: {product_id}")
        return product
    
    async def send_to_fix(self, product_id: int, comment: str) -> Product:
        """Отправить товар на доработку"""
        product = await self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_id}")
        
        product.status = ProductStatus.NEEDS_FIX
        product.moderator_comment = comment
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        logger.info(f"Товар отправлен на доработку: {product_id}")
        return product
    
    async def reject_product(self, product_id: int, reason: str) -> Product:
        """Отклонить товар"""
        product = await self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_id}")
        
        product.status = ProductStatus.REJECTED
        product.moderator_comment = reason
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        logger.info(f"Товар отклонен: {product_id}")
        return product
    
    async def update_stock(self, product_id: int, quantity: float) -> Product:
        """Обновить остаток товара"""
        product = await self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_id}")
        
        product.quantity_in_stock = quantity
        product.updated_at = datetime.utcnow()
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        return product
    
    async def update(self, product_id: int, **kwargs) -> Product:
        """Обновить товар"""
        product = await self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_id}")
        
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        return product
    
    async def delete(self, product_id: int) -> None:
        """Удалить товар"""
        product = await self.get_by_id(product_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
            logger.info(f"Товар удалён: {product_id}")
    
    async def search_approved(
        self,
        product_name_id: int = None,
        showcase_id: int = None,
        min_price: float = None,
        max_price: float = None,
    ) -> list[Product]:
        """Поиск одобренных товаров"""
        conditions = [Product.status == ProductStatus.APPROVED]
        
        if product_name_id:
            conditions.append(Product.product_name_id == product_name_id)
        if showcase_id:
            conditions.append(Product.showcase_id == showcase_id)
        if min_price:
            conditions.append(Product.price_per_kg >= min_price)
        if max_price:
            conditions.append(Product.price_per_kg <= max_price)
        
        stmt = select(Product).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalars().all()