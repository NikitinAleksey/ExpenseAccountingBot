from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import logged
from app.db import Base
from app.db.repositories.base import BaseRepository


@logged()
class LimitsRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: Base):
        """
        Добавляет новый элемент в базу данных.

        :param session: AsyncSession - сессия для взаимодействия с базой данных.
        :param item: Base - элемент для добавления в базу данных.
        :return: добавленный элемент.
        """
        cls.log.info(f"Метод create. Добавление нового элемента: {item}.")
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Base):
        """
        Читает элемент из базы данных по tg_id и модели.

        :param session: AsyncSession - сессия для взаимодействия с базой данных.
        :param tg_id: int - идентификатор пользователя в Telegram.
        :param model: Base - модель для чтения данных.
        :return: найденный элемент или None.
        """
        cls.log.info(f"Метод read. Чтение элемента для {tg_id=} из модели: {model}.")
        stmt = select(model).where(model.user_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, item: Base):
        """
        Обновляет элемент в базе данных.

        :param session: AsyncSession - сессия для взаимодействия с базой данных.
        :param item: Base - элемент для обновления в базе данных.
        :return: обновленный элемент.
        """
        cls.log.info(f"Метод update. Обновление элемента: {item}.")
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        """
        Удаляет элемент из базы данных (не реализовано).

        :param session: AsyncSession - сессия для взаимодействия с базой данных.
        :param item: Base - элемент для удаления.
        :return: None.
        """
        cls.log.info(f"Метод delete. Удаление элемента: {item}.")
        pass
