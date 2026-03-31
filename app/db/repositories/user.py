"""
Repository для работы с пользователями
"""
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.db.models.user import User, UserRole
from loguru import logger


class UserRepository:
    """CRUD операции для пользователей"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, first_name: str = None, username: str = None) -> User:
        """Получить пользователя или создать, если не существует"""
        # Ищем существующего
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Обновляем данные, если они изменились
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            if username and user.username != username:
                user.username = username
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        # Создаём нового
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            is_buyer=False,
            is_seller=False,
            is_admin=False,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Создан новый пользователь: {telegram_id}")
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Получить пользователя по telegram_id"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_buyer_role(self, user_id: int) -> User:
        """Добавить роль покупателя"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_buyer = True
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def set_seller_role(self, user_id: int) -> User:
        """Добавить роль продавца"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_seller = True
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def set_admin_role(self, user_id: int) -> User:
        """Добавить роль администратора"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_admin = True
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def block_user(self, user_id: int, reason: str = None) -> None:
        """Заблокировать пользователя"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_blocked = True
            self.session.add(user)
            await self.session.commit()
            logger.warning(f"Пользователь заблокирован: {user_id} ({reason})")

    async def unblock_user(self, user_id: int) -> None:
        """Разблокировать пользователя"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_blocked = False
            self.session.add(user)
            await self.session.commit()

    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_users(self) -> int:
        """Количество пользователей"""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
