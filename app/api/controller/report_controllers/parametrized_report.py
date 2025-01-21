from collections import defaultdict
from copy import copy
from datetime import datetime
from typing import Literal, Type, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.servises import XLSXBuilder, PDFBuilder, XMLBuilder
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

    def __init__(
            self,
            tg_id: int,
            mapping: dict,
            template: dict,
            models: list[BaseArticle],
            async_session: Callable[[], sessionmaker],
            start: datetime,
            end: datetime,
            dates_str_without_timezone: str,
            group_type: Literal['article_group_type', 'period_group_type'],
            group_type_period: Literal['year_group_type', 'month_group_type'],
            file_type: str
    ):
        self.tg_id = tg_id
        self.mapping = mapping
        self.template = template
        self.models = models
        self.session = async_session
        self.start = start
        self.end = end
        self.dates_str_without_timezone = dates_str_without_timezone
        self.group_type = group_type
        self.group_type_method = getattr(self, self.group_type)
        self.group_type_period = group_type_period
        self.file_type_method = getattr(self, file_type)

    async def launch(self):
        self.log.info(f'Метод get_parametrized_report. '
                      f'Запуск отчета c параметрами для {self.tg_id=}, {self.start=}, {self.end=} {self.group_type_method=}.')
        expenses, limits = await self._get_expenses_and_limits()
        expenses, limits = self._translate(expenses=expenses, limits=limits)
        self.log.debug(f'В ПАРАМЕТРИЗИРОВАННОМ ЗАПРОСЕ ПОЛУЧИЛИ: \n{expenses=}\n{limits=}')
        self.log.debug(f'Метод get_parametrized_report. Builder: {self.file_type_method}')

        builder = self.file_type_method()
        file_path = builder(expenses=expenses, limits=limits, tg_id=self.tg_id).generate_report()
        return file_path

    async def _get_expenses_and_limits(self):
        async with self.session as session:
            limits = await self._limits(session=session)
            expenses = await self.group_type_method(session=session)

        return expenses, limits

    async def _limits(self, session: AsyncSession):
        if self.group_type == 'article_group_type':
            months_quantity = self.months_between()
        else:
            if self.group_type_period == 'year_group_type':
                months_quantity = 12
            else:
                months_quantity = 1

        limits_record = await self._limits_repository.read(
            session=session,
            tg_id=self.tg_id,
            model=self._limits_model
        )
        if limits_record:
            limits = limits_record.__dict__
            for key, val in limits.items():
                if isinstance(val, int):
                    limits[key] = val * months_quantity
            self.log.debug(f'Метод limits. Лимиты для {self.tg_id=}: {limits}.')
            return limits
        else:
            self.log.warning(f'Метод limits. Лимиты для {self.tg_id=} не найдены.')

    def months_between(self):
        delta_years = self.end.year - self.start.year
        delta_months = self.end.month - self.start.month
        quantity = delta_years * 12 + delta_months
        return quantity if quantity > 0 else 1

    async def article_group_type(self, session: AsyncSession):
        self.log.debug(f'Метод article_group_type. Получаем сумму для моделей.')

        expenses = await self._article_repository.get_aggregated_articles_by_start_end_period(
            session=session,
            tg_id=self.tg_id,
            models=self.models,
            start=self.start,
            end=self.end,
            dates_str_without_timezone=self.dates_str_without_timezone
        )

        return expenses

    async def period_group_type(self, session: AsyncSession):
        kwargs = {'session': session, 'tg_id': self.tg_id, 'models': self.models, 'start': self.start, 'end': self.end}

        if self.group_type_period == 'year_group_type':
            return await self._article_repository.get_aggregated_articles_by_start_end_period_by_years(**kwargs)
        else:
            return await self._article_repository.get_aggregated_articles_by_start_end_period_by_months(**kwargs)

    def _build_article_report_data(cls, expenses: dict, limits: dict, mapping: dict, period: str):
        cls.log.debug(f'Метод _build_parametrized_report_data. Создаем словарь с затратами и лимитами.')
        data = {period: {}}
        for key, value in mapping.items():
            expense = expenses.get(value)
            limit = limits.get(value)
            data[period][key.capitalize()] = {
                'Сумма затрат': expense if expenses else 0,
                'Лимит': limit if limit else 0
            }
        cls.log.debug(f'Метод _build_parametrized_report_data. Словарь с затратами и лимитами готов {data=}.')

        return data

    def _translate(self, expenses: list[tuple], limits: dict):
        translated_expenses = []
        for record in expenses:
            translated_record = (*record[:-1], self.mapping[record[-1]])
            translated_expenses.append(translated_record)

        translated_limits = {}
        for key, val in limits.items():
            translated_key = self.mapping.get(key)
            if translated_key:
                translated_limits[translated_key] = val

        return translated_expenses, translated_limits

    @staticmethod
    def to_xml():
        return XMLBuilder

    @staticmethod
    def to_pdf():
        return PDFBuilder

    @staticmethod
    def to_xlsx():
        return XLSXBuilder

