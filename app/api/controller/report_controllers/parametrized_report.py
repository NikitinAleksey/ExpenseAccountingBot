from datetime import datetime
from typing import Callable, Literal, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.servises import PDFBuilder, XLSXBuilder, XMLBuilder
from app.db import BaseArticle, MonthlyLimits
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.db.repositories.monthly_limits import LimitsRepository
from app.utils import logged

__all__ = ["ParametrizedReport"]


@logged()
class ParametrizedReport:
    """
    Класс для генерации параметризованных отчетов с использованием различных шаблонов
    и типов группировки (по статьям или периодам).

    Атрибуты:
        _article_repository: Репозиторий для работы с расходами.
        _limits_repository: Репозиторий для работы с лимитами.
        _limits_model: Модель лимитов.
    """

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
        group_type: Literal["article_group_type", "period_group_type"],
        group_type_period: Literal["year_group_type", "month_group_type"],
        file_type: str,
    ):
        """
        Инициализирует объект отчета с параметрами.

        :param tg_id: ID пользователя в Telegram.
        :param mapping: Словарь для отображения данных.
        :param template: Шаблон для отчета.
        :param models: Модели для расчета данных.
        :param async_session: Функция для создания сессии.
        :param start: Дата начала периода.
        :param end: Дата окончания периода.
        :param dates_str_without_timezone: Даты без учета часового пояса.
        :param group_type: Тип группировки данных (по статье или периоду).
        :param group_type_period: Период для группировки (по годам или месяцам).
        :param file_type: Тип файла для вывода отчета.
        """
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
        """
        Запускает генерацию параметризованного отчета.

        :return: Путь к сгенерированному отчету.
        """
        self.log.info(
            f"Метод get_parametrized_report. "
            f"Запуск отчета c параметрами для {self.tg_id=}, {self.start=}, {self.end=} {self.group_type_method=}."
        )
        expenses, limits = await self._get_expenses_and_limits()
        expenses, limits = self._translate(expenses=expenses, limits=limits)
        self.log.debug(
            f"В ПАРАМЕТРИЗИРОВАННОМ ЗАПРОСЕ ПОЛУЧИЛИ: \n{expenses=}\n{limits=}"
        )
        self.log.debug(
            f"Метод get_parametrized_report. Builder: {self.file_type_method}"
        )

        builder = self.file_type_method()
        file_path = builder(
            expenses=expenses, limits=limits, tg_id=self.tg_id
        ).generate_report()
        return file_path

    async def _get_expenses_and_limits(self):
        """
        Получает данные о расходах и лимитах для отчета.

        :return: Кортеж с данными о расходах и лимитах.
        """
        async with self.session as session:
            limits = await self._limits(session=session)
            expenses = await self.group_type_method(session=session)

        return expenses, limits

    async def _limits(self, session: AsyncSession):
        """
        Получает лимиты для пользователя, учитывая тип группировки.

        :param session: Сессия для работы с базой данных.
        :return: Лимиты для пользователя.
        """
        if self.group_type == "article_group_type":
            months_quantity = self.months_between()
        else:
            if self.group_type_period == "year_group_type":
                months_quantity = 12
            else:
                months_quantity = 1

        limits_record = await self._limits_repository.read(
            session=session, tg_id=self.tg_id, model=self._limits_model
        )
        if limits_record:
            limits = limits_record.__dict__
            for key, val in limits.items():
                if isinstance(val, int):
                    limits[key] = val * months_quantity
            self.log.debug(f"Метод limits. Лимиты для {self.tg_id=}: {limits}.")
            return limits
        else:
            self.log.warning(f"Метод limits. Лимиты для {self.tg_id=} не найдены.")

    def months_between(self):
        """
        Вычисляет количество месяцев между началом и концом периода.

        :return: Количество месяцев.
        """
        delta_years = self.end.year - self.start.year
        delta_months = self.end.month - self.start.month
        quantity = delta_years * 12 + delta_months
        return quantity if quantity > 0 else 1

    async def article_group_type(self, session: AsyncSession):
        """
        Получает агрегированные данные по расходам для группировки по статьям.

        :param session: Сессия для работы с базой данных.
        :return: Данные о расходах.
        """
        self.log.debug(f"Метод article_group_type. Получаем сумму для моделей.")

        expenses = (
            await self._article_repository.get_aggregated_articles_by_start_end_period(
                session=session,
                tg_id=self.tg_id,
                models=self.models,
                start=self.start,
                end=self.end,
                dates_str_without_timezone=self.dates_str_without_timezone,
            )
        )

        return expenses

    async def period_group_type(self, session: AsyncSession):
        """
        Получает агрегированные данные по расходам для группировки по периодам (по годам или месяцам).

        :param session: Сессия для работы с базой данных.
        :return: Данные о расходах.
        """
        kwargs = {
            "session": session,
            "tg_id": self.tg_id,
            "models": self.models,
            "start": self.start,
            "end": self.end,
        }

        if self.group_type_period == "year_group_type":
            return await self._article_repository.get_aggregated_articles_by_start_end_period_by_years(
                **kwargs
            )
        else:
            return await self._article_repository.get_aggregated_articles_by_start_end_period_by_months(
                **kwargs
            )

    def _build_article_report_data(
        cls, expenses: dict, limits: dict, mapping: dict, period: str
    ):
        """
        Строит данные для отчета по статьям расходов.

        :param expenses: Словарь с расходами.
        :param limits: Словарь с лимитами.
        :param mapping: Словарь с отображением.
        :param period: Период отчета.
        :return: Словарь с данными для отчета.
        """
        cls.log.debug(
            f"Метод _build_parametrized_report_data. Создаем словарь с затратами и лимитами."
        )
        data = {period: {}}
        for key, value in mapping.items():
            expense = expenses.get(value)
            limit = limits.get(value)
            data[period][key.capitalize()] = {
                "Сумма затрат": expense if expenses else 0,
                "Лимит": limit if limit else 0,
            }
        cls.log.debug(
            f"Метод _build_parametrized_report_data. Словарь с затратами и лимитами готов {data=}."
        )

        return data

    def _translate(self, expenses: list[tuple], limits: dict):
        """
        Переводит данные расходов и лимитов согласно отображению.

        :param expenses: Список расходов.
        :param limits: Словарь с лимитами.
        :return: Переведенные данные расходов и лимитов.
        """
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
        """
        Возвращает класс для генерации отчета в формате XML.

        :return: Класс XMLBuilder.
        """
        return XMLBuilder

    @staticmethod
    def to_pdf():
        """
        Возвращает класс для генерации отчета в формате PDF.

        :return: Класс PDFBuilder.
        """
        return PDFBuilder

    @staticmethod
    def to_xlsx():
        """
        Возвращает класс для генерации отчета в формате XLSX.

        :return: Класс XLSXBuilder.
        """
        return XLSXBuilder
