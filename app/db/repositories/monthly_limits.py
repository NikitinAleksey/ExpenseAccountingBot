from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import logged
from app.db import Base
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


@logged()
class LimitsRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: Base):
        cls.log.info(f"Метод create. Добавление нового элемента: {item}.")
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Base):
        cls.log.info(f"Метод read. Чтение элемента для {tg_id=} из модели: {model}.")
        stmt = select(model).where(model.user_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, item: Base):
        cls.log.info(f"Метод update. Обновление элемента: {item}.")
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        cls.log.info(f"Метод delete. Удаление элемента: {item}.")
        pass
