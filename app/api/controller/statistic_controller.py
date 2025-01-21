import calendar
from datetime import datetime, timedelta
from typing import Literal

import pydantic

from app.api.servises.validators.validators import YearValidator, MonthValidator, DayValidator
from app.db.repositories.monthly_limits import LimitsRepository
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.db.models import BaseArticle, User, MonthlyLimits
from app.db.repositories.user import UserRepository
from app.api.controller import BaseController
from app.api.controller.report_controllers import FastReport, ParametrizedReport
from app.utils import logged


@logged()
class StatisticController(BaseController):
    _limits_repository = LimitsRepository
    _article_repository = ExpenseArticleRepository
    _user_repository = UserRepository
    _limits_model = MonthlyLimits
    _article_model = BaseArticle
    _user_model = User
    _year_validator = YearValidator
    _month_validator = MonthValidator
    _day_validator = DayValidator

    def __init__(self, tg_id: int, mapping: dict, report_type: Literal['fast', 'parametrized'], user: User, template: dict = None):
        self.tg_id = tg_id
        self.start = datetime(year=2024, month=1, day=1)
        self.end = datetime(year=datetime.utcnow().year, month=12, day=31)
        self.user = user
        self.report_type = report_type
        self.target_state = None
        self.group_type = None
        self.group_type_period = None
        self.mapping = mapping
        self.template = template
        self.file_type = None

    def set_year(self, year: str, edge: Literal['start', 'end']):
        self.log.debug(f'Метод set_year. Устанавливаем год {year=} для {edge=}')
        try:
            validated_year = self._year_validator(year=year)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            self.log.debug(f'Метод set_year. Произошла ошибка валидации {ctx_error_message=}')
            return str(ctx_error_message)
        if edge == 'start':
            self.start = self.start.replace(year=validated_year.year)
        else:
            self.end = self.end.replace(year=validated_year.year)
        self.log.debug(f'Метод set_year. Год {year=} для {edge=} установлен.')

    def set_month(self, month: str, edge: Literal['start', 'end']):
        self.log.debug(f'Метод set_month. Устанавливаем месяц {month=} для {edge=}.')
        try:
            validated_month = self._month_validator(month=month)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            self.log.debug(f'Метод set_month. Произошла ошибка валидации {ctx_error_message=}.')
            return str(ctx_error_message)
        if edge == 'start':
            self.start = self.start.replace(month=validated_month.month)
        else:
            _, last_day = calendar.monthrange(self.end.year, validated_month.month)
            self.end = self.end.replace(month=validated_month.month, day=last_day)
        self.log.debug(f'Метод set_year. Месяц {month=} для {edge=} установлен.')

    def set_day(self, day: str, month: int, year: int, edge: Literal['start', 'end']):
        self.log.debug(f'Метод set_day. Устанавливаем день {day=} для {edge=}, {year=}, {month=}.')
        try:
            validated_day = self._day_validator(year=year, month=month, day=day)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            self.log.debug(f'Метод set_day. Произошла ошибка валидации {ctx_error_message=}.')
            return str(ctx_error_message)
        if edge == 'start':
            self.start = self.start.replace(day=validated_day.day)
        else:
            self.end = self.end.replace(day=validated_day.day)
        self.log.debug(f'Метод set_day. День {day=} для {edge=}, {year=}, {month=} установлен.')

    def set_group_type(self, group_type: str):
        self.log.debug(f'Метод set_group_type. Устанавливаем {group_type=}')

        self.group_type = group_type

    def set_file_type(self, file_type: str):
        self.file_type = file_type

    def set_group_type_period(self, group_type_period: str):
        self.log.debug(f'Метод set_group_type_period. Устанавливаем {group_type_period=} для {self.group_type=}')
        self.group_type_period = group_type_period

    def dates_repr(self):
        self.log.debug(f'Метод dates_repr. Форматируем даты для ответа пользователю.')
        return self.start.strftime("%d.%m.%Y"), self.end.strftime("%d.%m.%Y")

    def year_builder(self) -> list:
        self.log.debug(f'Метод year_builder. Строим список лет.')
        end_year = datetime.now().year
        return [str(year) for year in range(self.start.year, end_year + 1)]

    @staticmethod
    def day_builder(date: datetime):
        year = date.year
        month = date.month
        days_qnt = calendar.monthrange(year, month)[1]
        return [str(day) for day in range(1, days_qnt + 1)]

    async def get_report(self):
        self.log.info(f'Метод get_report. Запуск отчета для {self.tg_id=}, report_type={self.report_type}.')

        self.log.debug(f'Метод get_report. Начало отчета: {self.start=}, конец отчета: {self.end=}.')

        models = self._article_model.__subclasses__()
        self.log.debug(f'Метод get_report. Список моделей статей: {models}.')

        async_session = await self._get_connect()
        if self.report_type == 'fast':
            self.log.info(f'Метод get_report. Генерация быстрого отчета для {self.tg_id=}.')
            self.start = self._from_utc_to_timezone_dt(timezone=self.user.timezone)

            return await FastReport.get_fast_report(
                tg_id=self.tg_id,
                mapping=self.mapping,
                models=models,
                async_session=async_session,
                article_repository=self._article_repository,
                limits_repository=self._limits_repository,
                limits_model=self._limits_model,
                start=self.start
            )

        elif self.report_type == 'parametrized':
            self.log.info(f'Метод get_report. Генерация параметризованного отчета для {self.tg_id=}.')
            current = datetime.utcnow()
            self.end = self.end if self.end < current else current
            dates_str_without_timezone = f'{self.start.strftime("%d.%m.%Y")}-{self.end.strftime("%d.%m.%Y")}'
            self.start = self._from_utc_to_timezone_dt(timezone=self.user.timezone, utc_datetime=self.start)

            self.end = self._from_utc_to_timezone_dt(timezone=self.user.timezone, utc_datetime=self.end)

            report = ParametrizedReport(
                tg_id=self.tg_id,
                mapping=self.mapping,
                template=self.template,
                models=models,
                async_session=async_session,
                start=self.start,
                end=self.end,
                dates_str_without_timezone=dates_str_without_timezone,
                group_type=self.group_type,
                group_type_period=self.group_type_period,
                file_type=self.file_type
            )
            return await report.launch()

        else:
            self.log.error(f'Метод get_report. Неверный тип отчета: {self.report_type}.')
            raise ValueError('Неверный тип отчета.')

    def _from_utc_to_timezone_dt(self, timezone: int = 0, utc_datetime: datetime = None) -> datetime:
        """
        Метод получает время и дату (или None, тогда определяет текущую дату по utc) и вычитает из нее часовой пояс.
        Это нужно, чтобы корректно создавать временные промежутки для отчетов. Так как время в бд хранится в UTC.


        :param timezone: Часовой пояс пользователя из бд.
        :param utc_datetime: Дата и время границы периода, или None (тогда возьмется начало текущего месяца).
        :return: Нужный период с учетом timezone.
        """
        self.log.debug(f'Метод _from_utc_to_timezone_dt. Входные параметры: {utc_datetime=}, {timezone=}.')

        if not utc_datetime:
            utc_datetime = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)
            self.log.debug(f'Метод _from_utc_to_timezone_dt. Установлена дата: {utc_datetime=}.')

        timezone_datetime = utc_datetime - timedelta(hours=timezone)

        self.log.debug(f'Метод _from_utc_to_timezone_dt. После учета часового пояса: {timezone_datetime=}.')
        return timezone_datetime
