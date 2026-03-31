"""
Repository для справочников (товары, формы юрлица)
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.dict_product_name import ProductName
from app.db.models.dict_legal_form import LegalForm
from loguru import logger


class DictionaryRepository:
    """Операции со справочниками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === PRODUCT NAMES ===
    
    async def create_product_name(self, name: str, description: str = None) -> ProductName:
        """Создать наименование товара"""
        product = ProductName(name=name, description=description)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        logger.info(f"Создано наименование товара: {name}")
        return product
    
    async def get_product_name(self, product_name_id: int) -> ProductName | None:
        """Получить наименование товара"""
        stmt = select(ProductName).where(ProductName.id == product_name_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_product_names(self) -> list[ProductName]:
        """Получить все наименования товаров"""
        stmt = select(ProductName).order_by(ProductName.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_product_name(self, product_name_id: int, name: str = None, description: str = None) -> ProductName:
        """Обновить наименование товара"""
        product = await self.get_product_name(product_name_id)
        if not product:
            raise ValueError(f"Товар не найден: {product_name_id}")
        
        if name:
            product.name = name
        if description:
            product.description = description
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        
        return product
    
    async def delete_product_name(self, product_name_id: int) -> None:
        """Удалить наименование товара"""
        product = await self.get_product_name(product_name_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
            logger.info(f"Наименование товара удалено: {product_name_id}")
    
    # === LEGAL FORMS ===
    
    async def create_legal_form(self, name: str, code: str) -> LegalForm:
        """Создать форму юрлица"""
        form = LegalForm(name=name, code=code)
        self.session.add(form)
        await self.session.commit()
        await self.session.refresh(form)
        logger.info(f"Создана форма юрлица: {name}")
        return form
    
    async def get_legal_form(self, form_id: int) -> LegalForm | None:
        """Получить форму юрлица"""
        stmt = select(LegalForm).where(LegalForm.id == form_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_legal_forms(self) -> list[LegalForm]:
        """Получить все формы юрлица"""
        stmt = select(LegalForm).order_by(LegalForm.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_legal_form(self, form_id: int, name: str = None, code: str = None) -> LegalForm:
        """Обновить форму юрлица"""
        form = await self.get_legal_form(form_id)
        if not form:
            raise ValueError(f"Форма не найдена: {form_id}")
        
        if name:
            form.name = name
        if code:
            form.code = code
        
        self.session.add(form)
        await self.session.commit()
        await self.session.refresh(form)
        
        return form
    
    async def delete_legal_form(self, form_id: int) -> None:
        """Удалить форму юрлица"""
        form = await self.get_legal_form(form_id)
        if form:
            await self.session.delete(form)
            await self.session.commit()
            logger.info(f"Форма юрлица удалена: {form_id}")