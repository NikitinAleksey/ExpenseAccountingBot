import calendar
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.api.servises.mapping.mapping import (ExpenseArticleMapping,
                                              ExpenseLimitsArticleMapping)
from app.api.servises.texts.texts import texts

months = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
}


class ArticleValidator(BaseModel):
    article: str = Field(...)

    @field_validator("article")
    def validate_article(cls, value):
        """
        Проверяет, что статья расходов существует в списке доступных статей.

        :param value: str - статья расходов, которую нужно проверить.
        :return: str - возвращает статью расходов, если она допустима.
        :raises ValueError: если статья расходов не найдена в списке.
        """
        value = value.lower()
        allowed_expense_articles = ExpenseArticleMapping.data.keys()
        if value not in allowed_expense_articles:
            raise ValueError(
                "Статья расходов должна быть одной из имеющихся в списке ниже. Выберите статью:"
            )
        return value


class InsertValidator(ArticleValidator):
    amount: str = Field(...)

    @field_validator("amount")
    def validate_amount(cls, value):
        """
        Проверяет, что значение суммы является положительным числом.

        :param value: str - сумма, которую нужно проверить.
        :return: float - возвращает сумму как число с плавающей точкой.
        :raises ValueError: если сумма не является числом или меньше либо равна нулю.
        """
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Значение должно быть числом.")

        if value <= 0:
            raise ValueError("Значение должно быть больше нуля.")
        return value


class DeleteValidator(ArticleValidator):
    pass


class LimitsValidator(InsertValidator):
    @field_validator("article")
    def validate_article(cls, value):
        """
        Проверяет, что статья лимитов существует в списке доступных лимитов.

        :param value: str - статья лимитов, которую нужно проверить.
        :return: str - возвращает статью лимитов, если она допустима.
        :raises ValueError: если статья лимитов не найдена в списке.
        """
        value = value.lower()
        article_name = ExpenseLimitsArticleMapping.get_field_name_from_article_name(
            article_name=value
        )
        if not article_name:
            raise ValueError(
                "Статья лимитов должна быть одной из имеющихся в списке ниже. Выберите статью:"
            )
        return article_name


class YearValidator(BaseModel):
    year: Any

    @field_validator("year")
    def validate_year(cls, value):
        """
        Проверяет, что год является числом, больше 2023.

        :param value: Any - значение года, которое нужно проверить.
        :return: int - возвращает год как целое число.
        :raises ValueError: если год не является числом или меньше 2024.
        """
        try:
            value = int(value)
        except ValueError:
            raise ValueError("Год должен быть числом. Выберите год:")
        if value < 2024:
            raise ValueError("Год должен быть больше 2023. Выберите год:")
        return value


class MonthValidator(BaseModel):
    month: Any

    @field_validator("month")
    def validate_month(cls, value):
        """
        Проверяет, что месяц является допустимым значением.

        :param value: Any - месяц, который нужно проверить.
        :return: int - возвращает номер месяца.
        :raises ValueError: если месяц не найден в списке.
        """
        if value not in texts["reply_buttons"]["months"]:
            raise ValueError("Месяц должен быть месяцем, ало. Выберите месяц:")
        month_number = months.get(value.lower())
        return month_number


class DayValidator(BaseModel):
    year: int = Field(...)
    month: int = Field(...)
    day: Any

    @field_validator("day")
    def validate_day(cls, value, values):
        """
        Проверяет, что день является допустимым для указанного месяца и года.

        :param value: Any - день, который нужно проверить.
        :param values: dict - словарь с данными года и месяца.
        :return: int - возвращает день как целое число.
        :raises ValueError: если день не является числом или выходит за пределы допустимого диапазона.
        """
        data = values.data
        year = data["year"]
        month = data["month"]

        try:
            value = int(value)
        except ValueError:
            raise ValueError("День должен быть числом. Выберите день:")

        if not year or not month:
            raise ValueError("Год и месяц должны быть указаны для проверки дня.")

        max_days = calendar.monthrange(year, month)[1]

        if not 1 <= value <= max_days:
            raise ValueError(
                f"Некорректный день. Для {month:02}.{year} максимум {max_days} дней."
            )

        return value
