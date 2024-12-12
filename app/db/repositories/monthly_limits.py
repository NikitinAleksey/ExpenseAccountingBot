from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class LimitsRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: Base):
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Base):
        stmt = select(model).where(model.user_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def update(cls, session: AsyncSession, item: Base):
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        pass
