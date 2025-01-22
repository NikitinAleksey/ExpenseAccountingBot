from datetime import datetime
from typing import Type

from sqlalchemy import and_, desc, func, literal, union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import logged
from app.db import Base
from app.db.repositories.base import BaseRepository


@logged()
class ExpenseArticleRepository(BaseRepository):
    @classmethod
    async def create(cls, session: AsyncSession, item: Base):
        """
        Добавляет новый элемент в базу данных.

        :param session: AsyncSession - сессия базы данных.
        :param item: Base - элемент, который нужно добавить в базу данных.
        :return: добавленный элемент.
        """
        cls.log.info(f"Метод create. Добавление нового элемента в базу данных: {item}.")
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, user_id: int, model: Base):
        """
        Читает элемент по user_id для указанной модели.

        :param session: AsyncSession - сессия базы данных.
        :param user_id: int - идентификатор пользователя.
        :param model: Base - модель, для которой выполняется запрос.
        :return: первый найденный элемент.
        """
        cls.log.info(
            f"Метод read. Чтение элемента по user_id={user_id} для модели {model}."
        )
        stmt = select(model).where(model.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_last_hundred_records(
        cls,
        session: AsyncSession,
        tg_id: int,
        model: Base,
        limit: int = 50,
        offset: int = 0,
    ):
        """
        Получает последние записи для tg_id с учетом лимита и смещения.

        :param session: AsyncSession - сессия базы данных.
        :param tg_id: int - идентификатор пользователя.
        :param model: Base - модель, для которой выполняется запрос.
        :param limit: int - максимальное количество записей для выборки.
        :param offset: int - смещение для выборки.
        :return: список последних записей.
        """
        cls.log.info(
            f"Метод get_last_hundred_records. Получение последних {limit} записей для tg_id={tg_id}."
        )
        stmt = (
            select(model)
            .options(selectinload(model.user))
            .order_by(desc(model.updated_at))
            .limit(limit)
            .offset(offset)
            .where(model.user_id == tg_id)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_summ_from_article_by_user_and_start_period(
        cls, session: AsyncSession, tg_id: int, model: Type[Base], start: datetime
    ):
        """
        Получает сумму затрат для tg_id начиная с указанной даты.

        :param session: AsyncSession - сессия базы данных.
        :param tg_id: int - идентификатор пользователя.
        :param model: Type[Base] - модель, для которой выполняется запрос.
        :param start: datetime - дата начала периода.
        :return: сумма затрат.
        """
        cls.log.info(
            f"Метод get_summ_from_article_by_user_and_start_period. Получение суммы затрат для tg_id={tg_id} начиная с {start}."
        )
        stmt = select(func.sum(model.summ)).where(
            and_(model.user_id == tg_id, model.updated_at >= start)
        )
        result = await session.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def get_aggregated_articles_by_start_end_period(
        cls,
        session: AsyncSession,
        tg_id: int,
        models: list[Type[Base]],
        start: datetime,
        end: datetime,
        dates_str_without_timezone: str,
    ):
        """
        Получает сумму затрат для tg_id за указанный период.

        :param session: AsyncSession - сессия базы данных.
        :param tg_id: int - идентификатор пользователя.
        :param models: list[Type[Base]] - список моделей для выборки.
        :param start: datetime - дата начала периода.
        :param end: datetime - дата окончания периода.
        :param dates_str_without_timezone: str - строка даты без часового пояса.
        :return: агрегированные данные.
        """
        cls.log.info(
            f"Метод get_aggregated_articles_by_start_end_period. Получение суммы затрат для {tg_id=}"
            f" за период {start} - {end} ."
        )
        queries = []

        for model in models:
            stmt = select(
                literal(dates_str_without_timezone),
                func.sum(model.summ),
                literal(model.__tablename__),
            ).where(and_(model.user_id == tg_id, model.updated_at.between(start, end)))
            queries.append(stmt)
        combined_query = union(*queries)
        result = await session.execute(combined_query)
        return result.fetchall()

    @classmethod
    async def get_aggregated_articles_by_start_end_period_by_months(
        cls,
        session: AsyncSession,
        tg_id: int,
        models: list[Type[Base]],
        start: datetime,
        end: datetime,
    ):
        """
        Получает сумму затрат для tg_id за указанный период, сгруппированную по месяцам.

        :param session: AsyncSession - сессия базы данных.
        :param tg_id: int - идентификатор пользователя.
        :param models: list[Type[Base]] - список моделей для выборки.
        :param start: datetime - дата начала периода.
        :param end: datetime - дата окончания периода.
        :return: агрегированные данные по месяцам.
        """
        cls.log.info(
            f"Метод get_aggregated_articles_by_start_end_period_by_months. Получение суммы затрат для tg_id={tg_id} за период {start}-{end}."
        )

        queries = []
        for model in models:
            stmt = select(
                func.to_char(model.updated_at, "YYYY-MM"),
                model.summ,
                literal(model.__tablename__),
            ).where(and_(model.user_id == tg_id, model.updated_at.between(start, end)))
            queries.append(stmt)
        combined_query = union(*queries)
        result = await session.execute(combined_query)
        return result.fetchall()

    @classmethod
    async def get_aggregated_articles_by_start_end_period_by_years(
        cls,
        session: AsyncSession,
        tg_id: int,
        models: list[Type[Base]],
        start: datetime,
        end: datetime,
    ):
        """
        Получает сумму затрат для tg_id за указанный период, сгруппированную по годам.

        :param session: AsyncSession - сессия базы данных.
        :param tg_id: int - идентификатор пользователя.
        :param models: list[Type[Base]] - список моделей для выборки.
        :param start: datetime - дата начала периода.
        :param end: datetime - дата окончания периода.
        :return: агрегированные данные по годам.
        """
        cls.log.info(
            f"Метод get_aggregated_articles_by_start_end_period_by_years. Получение суммы затрат для tg_id={tg_id} за период {start} - {end}."
        )
        queries = []

        for model in models:
            stmt = select(
                func.to_char(model.updated_at, "YYYY"),
                model.summ,
                literal(model.__tablename__),
            ).where(and_(model.user_id == tg_id, model.updated_at.between(start, end)))

            queries.append(stmt)

        combined_query = union(*queries)
        result = await session.execute(combined_query)
        return result.fetchall()

    @classmethod
    async def update(cls, session: AsyncSession, item: Base):
        """
        Обновляет элемент в базе данных.

        :param session: AsyncSession - сессия базы данных.
        :param item: Base - элемент для обновления.
        :return: обновленный элемент.
        """
        cls.log.info(f"Метод update. Обновление элемента в базе данных: {item}.")
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        """
        Удаляет элемент из базы данных.

        :param session: AsyncSession - сессия базы данных.
        :param item: Base - элемент, который нужно удалить.
        :return: удаленный элемент.
        """
        cls.log.info(f"Метод delete. Удаление элемента: {item}.")
        await session.delete(item)
        await session.commit()
        return item
