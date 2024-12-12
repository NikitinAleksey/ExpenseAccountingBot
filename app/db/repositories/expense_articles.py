from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, desc
from sqlalchemy.orm import selectinload

from app.db import Base
from app.db.repositories.base import BaseRepository


class ExpenseArticleRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: Base):
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, user_id: int, model: Base):
        stmt = select(model).where(model.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_last_hundred_records(cls, session: AsyncSession, tg_id: int, model: Base, limit: int = 50, offset: int = 0):
        stmt = select(model).options(selectinload(model.user)).order_by(desc(model.updated_at)).limit(limit).offset(offset).where(model.user_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_all_records_by_user_and_period(cls, session: AsyncSession, tg_id: int, model: Type[Base], start):


    @classmethod
    async def update(cls, session: AsyncSession, item: Base):
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        await session.delete(item)
        await session.commit()
        return item

