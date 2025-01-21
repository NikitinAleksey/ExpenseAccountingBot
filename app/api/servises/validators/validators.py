import calendar
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.api.servises.mapping.mapping import ExpenseArticleMapping, ExpenseLimitsArticleMapping
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

    @field_validator('article')
    def validate_article(cls, value):
        value = value.lower()
        allowed_expense_articles = ExpenseArticleMapping.data.keys()
        if value not in allowed_expense_articles:
            raise ValueError("Статья расходов должна быть одной из имеющихся в списке ниже. Выберите статью:")
        return value


class InsertValidator(ArticleValidator):
    amount: str = Field(...)

    @field_validator('amount')
    def validate_amount(cls, value):
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
    @field_validator('article')
    def validate_article(cls, value):
        value = value.lower()
        article_name = ExpenseLimitsArticleMapping.get_field_name_from_article_name(article_name=value)
        if not article_name:
            raise ValueError("Статья лимитов должна быть одной из имеющихся в списке ниже. Выберите статью:")
        return article_name


class YearValidator(BaseModel):
    year: Any

    @field_validator('year')
    def validate_year(cls, value):
        try:
            value = int(value)
        except ValueError:
            raise ValueError("Год должен быть числом. Выберите год:")
        if value < 2024:
            raise ValueError("Год должен быть больше 2023. Выберите год:")
        return value


class MonthValidator(BaseModel):
    month: Any

    @field_validator('month')
    def validate_month(cls, value):
        if value not in texts['reply_buttons']['months']:
            raise ValueError("Месяц должен быть месяцем, ало. Выберите месяц:")
        month_number = months.get(value.lower())
        return month_number


class DayValidator(BaseModel):
    year: int = Field(...)
    month: int = Field(...)
    day: Any

    @field_validator('day')
    def validate_day(cls, value, values):
        data = values.data
        year = data['year']
        month = data['month']

        try:
            value = int(value)
        except ValueError:
            raise ValueError("День должен быть числом. Выберите день:")

        if not year or not month:
            raise ValueError("Год и месяц должны быть указаны для проверки дня.")

        max_days = calendar.monthrange(year, month)[1]

        if not 1 <= value <= max_days:
            raise ValueError(f"Некорректный день. Для {month:02}.{year} максимум {max_days} дней.")

        return value
