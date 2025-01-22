from datetime import datetime
from typing import Callable, Type

from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

from app.db import BaseArticle, MonthlyLimits
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.db.repositories.monthly_limits import LimitsRepository
from app.utils import logged

__all__ = ["FastReport"]


@logged()
class FastReport:
    @classmethod
    async def get_fast_report(
        cls,
        tg_id: int,
        mapping: dict,
        models: list[Type[BaseArticle]],
        async_session: Callable[[], sessionmaker],
        article_repository: Type[ExpenseArticleRepository],
        limits_repository: Type[LimitsRepository],
        limits_model: Type[MonthlyLimits],
        start: datetime = None,
    ):
        """
        Генерация быстрого отчета для пользователя.

        :param tg_id: ID пользователя в Telegram.
        :param mapping: Словарь с отображением статей расходов.
        :param models: Список моделей статей расходов.
        :param async_session: Функция для получения асинхронной сессии.
        :param article_repository: Репозиторий для статей расходов.
        :param limits_repository: Репозиторий для лимитов.
        :param limits_model: Модель лимитов.
        :param start: Дата начала отчетного периода.
        :return: Строка с отчетом в формате таблицы.
        """
        cls.log.info(
            f"Метод get_fast_report. Запуск быстрого отчета для {tg_id=}, {start=}."
        )

        expenses, limits = await cls._build_data_for_fast_report(
            tg_id=tg_id,
            models=models,
            async_session=async_session,
            article_repository=article_repository,
            limits_repository=limits_repository,
            limits_model=limits_model,
            start=start,
        )

        cls.log.debug(
            f"Метод get_fast_report. "
            f"Получены данные: расходы={expenses}, лимиты={limits}."
        )
        report_result = cls._build_fast_report_result(
            expenses=expenses, limits=limits, mapping=mapping
        )
        cls.log.debug("Метод get_fast_report. " f"Отчет сформирован.")
        return report_result

    @classmethod
    async def _build_data_for_fast_report(
        cls,
        tg_id: int,
        models: list[Type[BaseArticle]],
        async_session: Callable[[], sessionmaker],
        article_repository: Type[ExpenseArticleRepository],
        limits_repository: Type[LimitsRepository],
        limits_model: Type[MonthlyLimits],
        start: datetime,
    ):
        """
        Сбор данных для быстрого отчета.

        :param tg_id: ID пользователя в Telegram.
        :param models: Список моделей статей расходов.
        :param async_session: Функция для получения асинхронной сессии.
        :param article_repository: Репозиторий для статей расходов.
        :param limits_repository: Репозиторий для лимитов.
        :param limits_model: Модель лимитов.
        :param start: Дата начала отчетного периода.
        :return: Кортеж с расходами и лимитами.
        """
        cls.log.info(
            f"Метод build_data_for_fast_report. "
            f"Сбор данных для tg_id={tg_id}, start={start}."
        )

        expenses = {}
        limits = {}
        async with async_session as session:
            for model in models:
                cls.log.debug(
                    f"Метод build_data_for_fast_report. "
                    f"Получаем сумму для модели {model.__tablename__}."
                )

                amount = await article_repository.get_summ_from_article_by_user_and_start_period(
                    session=session, tg_id=tg_id, model=model, start=start
                )
                expenses[model.__tablename__] = round(amount) if amount else 0
                cls.log.debug(
                    f"Метод build_data_for_fast_report. "
                    f"Сумма для модели {model.__tablename__}: "
                    f"{expenses[model.__tablename__]}."
                )

            limits_record = await limits_repository.read(
                session=session, tg_id=tg_id, model=limits_model
            )
            if limits_record:
                limits = limits_record.__dict__
                cls.log.debug(
                    f"Метод build_data_for_fast_report. "
                    f"Лимиты для {tg_id=}: {limits}."
                )
            else:
                cls.log.warning(
                    f"Метод build_data_for_fast_report. "
                    f"Лимиты для {tg_id=} не найдены."
                )

        return expenses, limits

    @classmethod
    def _build_fast_report_result(cls, expenses: dict, limits: dict, mapping: dict):
        """
        Формирование итогового отчета.

        :param expenses: Расходы для каждой статьи.
        :param limits: Лимиты для каждой статьи.
        :param mapping: Словарь с отображением статей расходов.
        :return: Отчет в виде таблицы.
        """
        cls.log.info("Метод build_fast_report_result. Формирование итогового отчета.")

        headers = ["Статья расходов", "Сумма", "Лимит"]
        data = []
        for key in mapping.keys():
            eng_name = mapping[key]
            name = key.capitalize()[:14] + "..." if len(key) > 17 else key.capitalize()
            expense = expenses[eng_name]
            limit = limits[eng_name]
            line = (name, str(expense), str(limit))
            data.append(line)

        cls.log.debug(
            "Метод build_fast_report_result. "
            "Сформированы данные отчета, возвращаем пользователю."
        )
        return f"\n{tabulate(data, headers, tablefmt='double_outline')}"
