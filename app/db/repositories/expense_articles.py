from datetime import datetime
from typing import Literal, Type

from sqlalchemy import and_, delete, desc, func, literal, union
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
        cls.log.info(f"Метод create. Добавление нового элемента в базу данных: {item}.")
        session.add(item)
        await session.commit()
        return item

    @classmethod
    async def read(cls, session: AsyncSession, user_id: int, model: Base):
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
        cls.log.info(f"Метод update. Обновление элемента в базе данных: {item}.")
        merged_item = await session.merge(item)
        await session.commit()
        return merged_item

    @classmethod
    async def delete(cls, session: AsyncSession, item: Base):
        cls.log.info(f"Метод delete. Удаление элемента: {item}.")
        await session.delete(item)
        await session.commit()
        return item
