from datetime import datetime
from typing import Literal, Type, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.servises import XLSBuilder
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.db.repositories.monthly_limits import LimitsRepository
from app.utils import logged
from app.db import BaseArticle, MonthlyLimits, Base

__all__ = ['ParametrizedReport']


@logged()
class ParametrizedReport:
    _article_repository: Type[ExpenseArticleRepository] = ExpenseArticleRepository
    _limits_repository: Type[LimitsRepository] = LimitsRepository
    _limits_model: Type[MonthlyLimits] = MonthlyLimits

    @classmethod
    async def get_parametrized_report(
            cls,
            tg_id: int,
            mapping: dict,
            models: list[Type[BaseArticle]],
            async_session: Callable[[], sessionmaker],
            start: datetime,
            end: datetime,
            group_type: Literal['article_group_type', 'period_group_type'],
            group_type_period: Literal['year_group_type', 'month_group_type'] = None
    ):
        cls.log.info(
            f'Метод get_parametrized_report. Запуск отчета c параметрами для {tg_id=}, {start=}, {end=} {group_type=}.')
        expenses, limits = await cls._build_data_for_parametrized_report(
            tg_id=tg_id,
            models=models,
            async_session=async_session,
            start=start,
            end=end,
            group_type=group_type,
            group_type_period=group_type_period
        )
        cls.log.debug(f'В ПАРАМЕТРИЗИРОВАННОМ ЗАПРОСЕ ПОЛУЧИЛИ: \n{expenses=}\n{limits=}')
        data = cls._build_parametrized_report_data(expenses=expenses, limits=limits, mapping=mapping)
        # TODO подумать, как лучше: передавать дату в контроллер, там уточнять, какой тип файла нужен, и с контроллера
        #  вызывать нужный метод /// или сразу тут его вызывать??? Пока вызываю прям тут, но скорее всего надо поменять.

        file_path = XLSBuilder(data=data, tg_id=tg_id).launch()
        return file_path

    @classmethod
    def _build_parametrized_report_data(cls, expenses: dict, limits: dict, mapping: dict):
        cls.log.debug(f'Метод _build_parametrized_report_data. Создаем словарь с затратами и лимитами.')
        data = {}
        for key, value in mapping.items():
            expense = expenses.get(value)
            limit = limits.get(value)
            data[key.capitalize()] = {
                'Сумма затрат': expense if expenses else 0,
                'Лимит': limit if limit else 0
            }
        cls.log.debug(f'Метод _build_parametrized_report_data. Словарь с затратами и лимитами готов {data=}.')

        return data

    @classmethod
    async def _build_data_for_parametrized_report(
            cls,
            tg_id: int,
            models: list[Type[BaseArticle]],
            async_session: Callable[[], sessionmaker],
            start: datetime,
            end: datetime,
            group_type: Literal['article_group_type', 'period_group_type'],
            group_type_period: Literal['year_group_type', 'month_group_type'] = None

    ):
        async with async_session as session:

            if group_type == 'article_group_type':
                expenses = await cls._article_group_type(
                    session=session,
                    tg_id=tg_id,
                    start=start,
                    end=end,
                    models=models
                )

            elif group_type == 'period_group_type':
                expenses = await cls._period_group_type(
                    session=session,
                    tg_id=tg_id,
                    start=start,
                    end=end,
                    models=models,
                    group_type_period=group_type_period
                )

            limits = await cls._limits(tg_id=tg_id, session=session)

        return expenses, limits

    @classmethod
    async def _article_group_type(cls, session: AsyncSession, tg_id: int, models: list[Type[BaseArticle]],
                                  start: datetime, end: datetime):
        expenses = {}
        for model in models:
            cls.log.debug(f'Метод article_group_type. Получаем сумму для модели {model.__tablename__}.')

            amount = await cls._article_repository.get_aggregated_articles_by_start_end_period(
                session=session,
                tg_id=tg_id,
                model=model,
                start=start,
                end=end
            )
            expenses[model.__tablename__] = int(amount) if amount else 0
            cls.log.debug(f'Метод _article_group_type. '
                          f'Сумма для модели {model.__tablename__}: '
                          f'{expenses[model.__tablename__]}.')
        return expenses

    @classmethod
    async def _period_group_type(cls, session: AsyncSession, tg_id: int, models: list[Type[BaseArticle]],
                                 start: datetime, end: datetime,
                                 group_type_period: Literal['year_group_type', 'month_group_type'] = None):
        expenses = {}

        if group_type_period is None or group_type_period == 'year_group_type':
            for model in models:
                group_by_years = await cls._article_repository.get_aggregated_articles_by_start_end_period_by_years(
                    session=session,
                    tg_id=tg_id,
                    model=model,
                    start=start,
                    end=end
                )
                expenses[model.__tablename__] = group_by_years
        else:
            for model in models:
                group_by_months = await cls._article_repository.get_aggregated_articles_by_start_end_period_by_months(
                    session=session,
                    tg_id=tg_id,
                    model=model,
                    start=start,
                    end=end
                )
                expenses[model.__tablename__] = group_by_months

        return expenses

    @classmethod
    async def _limits(cls, tg_id: int, session: AsyncSession):
        limits_record = await cls._limits_repository.read(
            session=session,
            tg_id=tg_id,
            model=cls._limits_model
        )
        if limits_record:
            limits = limits_record.__dict__
            cls.log.debug(f'Метод limits. Лимиты для {tg_id=}: {limits}.')
            return limits
        else:
            cls.log.warning(f'Метод limits. Лимиты для {tg_id=} не найдены.')

    async def to_jpg(self):
        ...

    async def to_xml(self):
        ...

    async def to_pdf(self):
        ...

    async def to_xls(self):
        ...
