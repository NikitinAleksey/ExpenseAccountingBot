from datetime import datetime, timedelta

from app.db.connector import PostgresConnector
from app.db.repositories.monthly_limits import LimitsRepository
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.db.models import BaseArticle, User, MonthlyLimits
from app.db.repositories.user import UserRepository


class StatisticController:
    _connector = PostgresConnector()
    _limits_repository = LimitsRepository
    _article_repository = ExpenseArticleRepository
    _user_repository = UserRepository
    _limits_model = MonthlyLimits
    _article_model = BaseArticle
    _user_model = User

    @classmethod
    async def get_connect(cls):
        return cls._connector.async_session

    @classmethod
    async def get_fast_report(cls, tg_id: int, start: datetime = None, end: datetime = None):
        user = await cls.get_current_user(tg_id=tg_id)
        if user:
            user_timezone = user.timezone
        else:
            # TODO нормально обработать отсутствие пользователя
            return 'Пользователь с таким айди не зарегистрирован'
        start, end = cls.get_from_to_dates(timezone=user_timezone, start=start, end=end)


    @classmethod
    def get_from_to_dates(cls, timezone: int = 0, start: datetime = None, end: datetime = None):
        if not start:
            start = datetime(datetime.now().year, datetime.now().month, 1)
        if not end:
            end = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

        start += timedelta(hours=timezone)
        end += timedelta(hours=timezone)

        return start, end

    @classmethod
    async def get_current_user(cls, tg_id: int):
        async_session = await cls.get_connect()
        async with async_session() as session:
            user = await cls._user_repository.read(
                tg_id=tg_id,
                session=session,
                model=cls._user_model
            )
            return user
