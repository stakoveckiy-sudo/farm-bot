"""
Repository для работы с профилями продавцов
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.db.models.seller_profile import SellerProfile, SellerStatus
from app.db.models.subscription import Subscription, SubscriptionPlan
from loguru import logger


class SellerRepository:
    """CRUD операции для п��офилей продавцов"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_id: int) -> SellerProfile:
        """Создать профиль продавца"""
        profile = SellerProfile(
            user_id=user_id,
            status=SellerStatus.NONE,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        # Создаём подписку (FREE по умолчанию)
        subscription = Subscription(
            seller_profile_id=profile.id,
            plan=SubscriptionPlan.FREE,
        )
        self.session.add(subscription)
        await self.session.commit()
        
        logger.info(f"Создан профиль продавца: user_id={user_id}")
        return profile
    
    async def get_by_user_id(self, user_id: int) -> SellerProfile | None:
        """Получить профиль по user_id"""
        stmt = select(SellerProfile).where(SellerProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, profile_id: int) -> SellerProfile | None:
        """Получить профиль по ID"""
        stmt = select(SellerProfile).where(SellerProfile.id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_registration_data(
        self,
        user_id: int,
        company_name: str,
        legal_form_id: int,
        owner_name: str,
        inn_unp: str,
        owner_phone: str,
        passport_file: str,
        registration_cert_file: str,
    ) -> SellerProfile:
        """Обновить данные регистрации"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Профиль не найден для user_id={user_id}")
        
        profile.company_name = company_name
        profile.legal_form_id = legal_form_id
        profile.owner_name = owner_name
        profile.inn_unp = inn_unp
        profile.owner_phone = owner_phone
        profile.passport_file = passport_file
        profile.registration_cert_file = registration_cert_file
        profile.status = SellerStatus.PENDING
        profile.updated_at = datetime.utcnow()
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        logger.info(f"Данные продавца обновлены и отправлены на модерацию: user_id={user_id}")
        return profile
    
    async def get_pending_sellers(self) -> list[SellerProfile]:
        """Получить список продавцов на модерации"""
        stmt = select(SellerProfile).where(SellerProfile.status == SellerStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def approve_seller(self, profile_id: int) -> SellerProfile:
        """Одобрить продавца"""
        profile = await self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Профиль не найден: {profile_id}")
        
        profile.status = SellerStatus.APPROVED
        profile.approved_at = datetime.utcnow()
        profile.moderator_comment = None
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        logger.info(f"Продавец одобрен: {profile_id}")
        return profile
    
    async def send_to_fix(self, profile_id: int, comment: str) -> SellerProfile:
        """Отправить на доработку"""
        profile = await self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Профиль не найден: {profile_id}")
        
        profile.status = SellerStatus.NEEDS_FIX
        profile.moderator_comment = comment
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        logger.info(f"Продавец от��равлен на доработку: {profile_id}")
        return profile
    
    async def reject_seller(self, profile_id: int, reason: str) -> SellerProfile:
        """Отклонить продавца"""
        profile = await self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Профиль не найден: {profile_id}")
        
        profile.status = SellerStatus.REJECTED
        profile.moderator_comment = reason
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        logger.info(f"Продавец отклонен: {profile_id}")
        return profile
    
    async def block_seller(self, profile_id: int) -> SellerProfile:
        """Заблокировать продавца (например за неоплату)"""
        profile = await self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Профиль не найден: {profile_id}")
        
        profile.status = SellerStatus.BLOCKED
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        logger.info(f"Продавец заблокирован: {profile_id}")
        return profile