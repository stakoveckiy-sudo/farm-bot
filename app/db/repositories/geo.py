"""
Repository для географических справочников
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.dict_geo import Country, Region, City
from loguru import logger


class GeoRepository:
    """Операции с географией"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === COUNTRIES ===
    
    async def create_country(self, name: str, code: str, currency: str) -> Country:
        """Создать страну"""
        country = Country(name=name, code=code, currency=currency)
        self.session.add(country)
        await self.session.commit()
        await self.session.refresh(country)
        logger.info(f"Создана страна: {code} ({name})")
        return country
    
    async def get_country(self, country_id: int) -> Country | None:
        """Получить страну"""
        stmt = select(Country).where(Country.id == country_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_country_by_code(self, code: str) -> Country | None:
        """Получить страну по коду"""
        stmt = select(Country).where(Country.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_countries(self) -> list[Country]:
        """Получить все страны"""
        stmt = select(Country)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    # === REGIONS ===
    
    async def create_region(self, country_id: int, name: str) -> Region:
        """Создать регион"""
        region = Region(country_id=country_id, name=name)
        self.session.add(region)
        await self.session.commit()
        await self.session.refresh(region)
        logger.info(f"Создан регион: {name}")
        return region
    
    async def get_region(self, region_id: int) -> Region | None:
        """Получить регион"""
        stmt = select(Region).where(Region.id == region_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_regions_by_country(self, country_id: int) -> list[Region]:
        """Получить регионы страны"""
        stmt = select(Region).where(Region.country_id == country_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete_region(self, region_id: int) -> None:
        """Удалить регион"""
        region = await self.get_region(region_id)
        if region:
            await self.session.delete(region)
            await self.session.commit()
            logger.info(f"Регион удалён: {region_id}")
    
    # === CITIES ===
    
    async def create_city(self, region_id: int, name: str) -> City:
        """Создать город"""
        city = City(region_id=region_id, name=name)
        self.session.add(city)
        await self.session.commit()
        await self.session.refresh(city)
        logger.info(f"Создан город: {name}")
        return city
    
    async def get_city(self, city_id: int) -> City | None:
        """Получить город"""
        stmt = select(City).where(City.id == city_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_cities_by_region(self, region_id: int) -> list[City]:
        """Получить города региона"""
        stmt = select(City).where(City.region_id == region_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete_city(self, city_id: int) -> None:
        """Удалить город"""
        city = await self.get_city(city_id)
        if city:
            await self.session.delete(city)
            await self.session.commit()
            logger.info(f"Город удалён: {city_id}")