from typing import Type

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import logged
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


__all__ = ['UserRepository']


@logged()
class UserRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: User):
        cls.log.info(f'Метод create. Добавление нового пользователя с tg_id={item.tg_id}.')
        session.add(item)
        await session.commit()
        cls.log.info(f'Метод create. Пользователь с tg_id={item.tg_id} успешно добавлен.')
        return item

    @classmethod
    async def read(cls, session: AsyncSession, tg_id: int, model: Type[User]):
        cls.log.info(f'Метод read. Чтение пользователя с tg_id={tg_id}.')
        stmt = select(model).where(model.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_user_by_name(cls, session: AsyncSession, name: str, model: User):
        cls.log.info(f'Метод get_user_by_name. Поиск пользователя по имени: {name}.')
        stmt = select(model).where(model.name == name)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_all_users(cls, session: AsyncSession, model: User, limit: int = 100, offset: int = 0):
        cls.log.info(f'Метод get_all_users. Получение списка пользователей. Параметры: limit={limit}, offset={offset}.')
        stmt = select(model).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, item: User):
        cls.log.info(f'Метод update. Обновление пользователя с tg_id={item.tg_id}.')
        merged_item = await session.merge(item)
        await session.commit()
        cls.log.info(f'Метод update. Пользователь с tg_id={item.tg_id} успешно обновлен.')
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: User):
        cls.log.info(f'Метод delete. Удаление пользователя с tg_id={item.tg_id}.')
        await session.delete(item)
        await session.commit()
        cls.log.info(f'Метод delete. Пользователь с tg_id={item.tg_id} успешно удален.')
        return item.tg_id
