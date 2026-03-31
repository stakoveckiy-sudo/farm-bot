"""
Repository для работы с витринами
"""
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.db.models.showcase import Showcase
from loguru import logger


class ShowcaseRepository:
    """CRUD операции для витрин"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        seller_profile_id: int,
        name: str,
        country_id: int,
        region_id: int,
        city_id: int | None,
        is_wholesale: bool,
        is_retail: bool,
        is_delivery_available: bool,
        pickup_address: str | None,
        phone: str,
        logo_file: str | None = None,
        description: str | None = None,
    ) -> Showcase:
        """Создать витрину"""
        showcase = Showcase(
            seller_profile_id=seller_profile_id,
            name=name,
            country_id=country_id,
            region_id=region_id,
            city_id=city_id,
            is_wholesale=is_wholesale,
            is_retail=is_retail,
            is_delivery_available=is_delivery_available,
            pickup_address=pickup_address,
            phone=phone,
            logo_file=logo_file,
            description=description,
        )
        self.session.add(showcase)
        await self.session.commit()
        await self.session.refresh(showcase)
        
        logger.info(f"Создана витрина: {showcase.id} (продавец={seller_profile_id})")
        return showcase
    
    async def get_by_id(self, showcase_id: int) -> Showcase | None:
        """Получить витрину по ID"""
        stmt = select(Showcase).where(Showcase.id == showcase_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_seller(self, seller_profile_id: int) -> list[Showcase]:
        """Получить все витрины продавца"""
        stmt = select(Showcase).where(Showcase.seller_profile_id == seller_profile_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_by_seller(self, seller_profile_id: int) -> int:
        """Подсчитать витрины продавца"""
        stmt = select(Showcase).where(Showcase.seller_profile_id == seller_profile_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
    
    async def update(self, showcase_id: int, **kwargs) -> Showcase:
        """Обновить витрину"""
        showcase = await self.get_by_id(showcase_id)
        if not showcase:
            raise ValueError(f"Витрина не найдена: {showcase_id}")
        
        for key, value in kwargs.items():
            if hasattr(showcase, key):
                setattr(showcase, key, value)
        
        showcase.updated_at = datetime.utcnow()
        self.session.add(showcase)
        await self.session.commit()
        await self.session.refresh(showcase)
        
        logger.info(f"Витрина обновлена: {showcase_id}")
        return showcase
    
    async def delete(self, showcase_id: int) -> None:
        """Удалить витрину"""
        showcase = await self.get_by_id(showcase_id)
        if showcase:
            await self.session.delete(showcase)
            await self.session.commit()
            logger.info(f"Витрина удалена: {showcase_id}")
    
    async def search(
        self,
        country_id: int = None,
        region_id: int = None,
        city_id: int = None,
        is_wholesale: bool = None,
        is_retail: bool = None,
    ) -> list[Showcase]:
        """Поиск витрин по параметрам"""
        conditions = [Showcase.is_active == True]
        
        if country_id:
            conditions.append(Showcase.country_id == country_id)
        if region_id:
            conditions.append(Showcase.region_id == region_id)
        if city_id:
            conditions.append(Showcase.city_id == city_id)
        if is_wholesale is not None:
            conditions.append(Showcase.is_wholesale == is_wholesale)
        if is_retail is not None:
            conditions.append(Showcase.is_retail == is_retail)
        
        stmt = select(Showcase).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalars().all()