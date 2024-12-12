from typing import Type

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.base import BaseRepository


__all__ = ['UserRepository']


class UserRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: User):
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Type[User]):
        stmt = select(model).where(model.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_user_by_name(cls, session: AsyncSession, name: str, model: User):
        stmt = select(model).where(model.name == name)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_all_users(cls, session: AsyncSession, model: User, limit: int = 100, offset: int = 0):
        stmt = select(model).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, item: User):
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: User):
        await session.delete(item)
        await session.commit()
        return item.tg_id
