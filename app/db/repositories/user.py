from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import logged
from app.db.models.user import User
from app.db.repositories.base import BaseRepository

__all__ = ["UserRepository"]


@logged()
class UserRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: User):
        """
        Добавляет нового пользователя в базу данных.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: User - объект пользователя для добавления.
        :return: возвращает добавленного пользователя.
        """
        cls.log.info(
            f"Метод create. Добавление нового пользователя с tg_id={item.tg_id}."
        )
        session.add(item)
        await session.commit()
        cls.log.info(
            f"Метод create. Пользователь с tg_id={item.tg_id} успешно добавлен."
        )
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Type[User]):
        """
        Читает пользователя из базы данных по tg_id.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param tg_id: int - ID пользователя в Telegram.
        :param model: Type[User] - модель пользователя для выборки.
        :return: возвращает найденного пользователя или None.
        """
        cls.log.info(f"Метод read. Чтение пользователя с tg_id={tg_id}.")
        stmt = select(model).where(model.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_user_by_name(cls, session: AsyncSession, name: str, model: User):
        """
        Поиск пользователя по имени.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param name: str - имя пользователя для поиска.
        :param model: User - модель пользователя для выборки.
        :return: возвращает найденного пользователя или None.
        """
        cls.log.info(f"Метод get_user_by_name. Поиск пользователя по имени: {name}.")
        stmt = select(model).where(model.name == name)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_all_users(
        cls, session: AsyncSession, model: User, limit: int = 100, offset: int = 0
    ):
        """
        Получает список пользователей с возможностью пагинации.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param model: User - модель пользователя для выборки.
        :param limit: int - количество пользователей для выборки.
        :param offset: int - смещение для пагинации.
        :return: возвращает список пользователей.
        """
        cls.log.info(
            f"Метод get_all_users. Получение списка пользователей. Параметры: "
            f"limit={limit}, offset={offset}."
        )
        stmt = select(model).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, item: User):
        """
        Обновляет информацию о пользователе.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: User - объект пользователя для обновления.
        :return: возвращает обновленного пользователя.
        """
        cls.log.info(f"Метод update. Обновление пользователя с tg_id={item.tg_id}.")
        merged_item = await session.merge(item)
        await session.commit()
        cls.log.info(
            f"Метод update. Пользователь с tg_id={item.tg_id} успешно обновлен."
        )
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: User):
        """
        Удаляет пользователя из базы данных.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: User - объект пользователя для удаления.
        :return: возвращает tg_id удаленного пользователя.
        """
        cls.log.info(f"Метод delete. Удаление пользователя с tg_id={item.tg_id}.")
        await session.delete(item)
        await session.commit()
        cls.log.info(f"Метод delete. Пользователь с tg_id={item.tg_id} успешно удален.")
        return item.tg_id
