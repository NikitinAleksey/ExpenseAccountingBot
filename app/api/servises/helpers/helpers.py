import calendar
from datetime import datetime

import pydantic

from app.api.servises.validators.validators import YearValidator, MonthValidator, DayValidator

__all__ = ['year_builder', 'day_builder', 'create_correct_dates']


def year_builder(start_year: int = 2024) -> list:
    end_year = datetime.now().year
    return [str(year) for year in range(start_year, end_year + 1)]


def day_builder(year: int, month: int):
    days_qnt = calendar.monthrange(year, month)[1]
    return [str(day) for day in range(1, days_qnt + 1)]


def create_correct_dates(dates: dict):
    start_year = dates['years']['start']
    start_month = dates['months']['start']
    start_day = dates['days']['start']

    end_year = dates['years']['end']
    end_month = dates['months']['end']
    end_day = dates['days']['end']

    start_year = int(start_year)
    start_month = int(start_month) if start_month else 1
    start_day = int(start_day) if start_day else 1

    end_year = int(end_year)
    end_month = int(end_month) if end_month else 1
    end_day = int(end_day) if end_day else calendar.monthrange(end_year, end_month)[1]

    start_date = create_correct_date(
        year=start_year,
        month=start_month,
        day=start_day
    )
    end_date = create_correct_date(
        year=end_year,
        month=end_month,
        day=end_day
    )
    return start_date, end_date


def create_correct_date(year: int, month: int, day: int):
    return datetime(year, month, day).strftime("%d.%m.%Y")


def validate_data(field: str, value: int | str, year: int = None, month: int = None):
    try:
        if field == 'year':
            validated_data = YearValidator(year=value)
        elif field == 'month':
            validated_data = MonthValidator(month=value)
        else:
            validated_data = DayValidator(day=value, year=year, month=month)
        return validated_data
    except pydantic.ValidationError as exc:
        ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
        return str(ctx_error_message)
