from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base


class BaseRepository(ABC):
    @abstractmethod
    async def create(self, session: AsyncSession, item: Base):
        """
        Создает новый элемент в базе данных.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: Base - объект для сохранения в базе данных.
        :return: None.
        """
        pass

    @abstractmethod
    async def read(self, session: AsyncSession, tg_id: int, model: Base):
        """
        Читает данные из базы данных по tg_id и модели.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param tg_id: int - ID пользователя для фильтрации данных.
        :param model: Base - модель, к которой относится запрос.
        :return: объект модели или None, если данные не найдены.
        """
        pass

    @abstractmethod
    async def update(self, session: AsyncSession, item: Base):
        """
        Обновляет данные элемента в базе данных.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: Base - объект с обновленными данными.
        :return: None.
        """
        pass

    @abstractmethod
    async def delete(self, session: AsyncSession, item: Base):
        """
        Удаляет элемент из базы данных.

        :param session: AsyncSession - асинхронная сессия для работы с базой данных.
        :param item: Base - объект, который необходимо удалить.
        :return: None.
        """
        pass
