from collections import OrderedDict
from datetime import timedelta

import pydantic

from app.api.controller import BaseController
from app.api.servises.mapping.mapping import ExpenseArticleMapping
from app.api.servises.validators.validators import (ArticleValidator,
                                                    InsertValidator)

from app.db.models import BaseArticle
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.utils import logged


@logged()
class ExpensesController(BaseController):
    """Контроллер для работы с затратами. Служит промежуточным слоем между роутером
    и репозиторием.
    """
    _repository = ExpenseArticleRepository
    _model: type[BaseArticle] | None = None

    @classmethod
    def get_model(cls, article_name: str) -> None:
        """По названию статьи на русском языке получает нужную модель БД."""
        cls._model = ExpenseArticleMapping.get_class_from_article_name(
            article_name=article_name
        )
        cls.log.info(f"Метод get_model. Получена модель затрат: {cls._model}.")

    @classmethod
    def make_a_dict(
        cls, records: list[BaseArticle]
    ) -> OrderedDict[BaseArticle, str] | None:
        """Создает словарь из записей о затратах, форматируя дату с учетом
        часового пояса пользователя.
        """
        cls.log.info("Метод make_a_dict. Создаем словарь.")

        if not records:
            return None
        formatted_records = OrderedDict()
        user_timezone = records[0].user.timezone
        for record in records:
            dt_with_offset = record.updated_at + timedelta(hours=user_timezone)
            formatted_time_with_offset = dt_with_offset.strftime("%d.%m.%Y %H:%M")
            formatted_records[record] = (
                f"Сумма: {record.summ}\nДата: {formatted_time_with_offset}"
            )
        return formatted_records

    @classmethod
    def extract_article_id_from_dict(
        cls, articles_dict: OrderedDict[BaseArticle, str], article_value: str
    ) -> BaseArticle | None:
        """Ищет ID статьи по ее значению в словаре статей."""
        cls.log.info(
            f"Метод extract_article_id_from_dict. Поиск id затраты для значения: {article_value}."
        )
        for key in articles_dict.keys():
            if articles_dict[key] == article_value:
                cls.log.info(
                    f"Метод extract_article_id_from_dict. Найдено соответствие для {article_value}: {key}."
                )
                return key
        cls.log.info(
            f"Метод extract_article_id_from_dict. Не найдено соответствия для {article_value}."
        )
        return None

    @classmethod
    async def add_expense(
        cls, tg_id: int, article_name: str, amount: str
    ) -> BaseArticle | str:
        """Добавляет новую затратную статью после валидации данных."""
        cls.log.info(
            f"Метод add_expense. Запуск с параметрами: {tg_id=}, {article_name=}, {amount=}."
        )
        try:
            validated_data = InsertValidator(amount=amount, article=article_name)
            cls.log.info(
                f"Метод add_expense. Валидация успешна для: {validated_data.amount}."
            )
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]["ctx"]["error"].args[0]
            cls.log.error(f"Метод add_expense. Ошибка валидации: {ctx_error_message}.")
            return str(ctx_error_message)

        cls.get_model(article_name=validated_data.article)

        async_session = await cls._get_connect()
        async with async_session as session:
            new_expense_article = cls._model(user_id=tg_id, summ=validated_data.amount)
            record = await cls._repository.create(
                session=session, item=new_expense_article
            )
            cls.log.info(
                f"Метод add_expense. Успешно добавлена новая затратная статья: {tg_id=}, {validated_data.amount=}, {cls._model=}."
            )
            return record

    @classmethod
    async def delete_expense(
        cls, articles_dict: OrderedDict[BaseArticle, str], article_value: str
    ) -> BaseArticle | None:
        """Удаляет статью затрат, если она найдена в словаре."""
        cls.log.info(f"Метод delete_expense. Запуск удаления статьи: {article_value}.")

        article = cls.extract_article_id_from_dict(
            articles_dict=articles_dict, article_value=article_value
        )
        if not article:
            cls.log.warning(
                f"Метод delete_expense. Не найдено соответствующее значение для удаления: {article_value}."
            )
            return None

        async_session = await cls._get_connect()
        async with async_session as session:
            delete_item = await ExpenseArticleRepository.delete(
                session=session, item=article
            )
            cls.log.info(f"Метод delete_expense. Затрата удалена: {article}.")
            return delete_item

    @classmethod
    async def get_expenses(
        cls, tg_id: int, article_name: str
    ) -> OrderedDict[BaseArticle, str] | str:
        """Получает последние 100 записей о затратах пользователя."""
        try:
            validated_data = ArticleValidator(article=article_name)
            cls.log.info(
                f"Метод get_expenses. Валидация успешна для статьи: {validated_data.article}."
            )
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]["ctx"]["error"].args[0]
            cls.log.error(f"Метод get_expenses. Ошибка валидации: {ctx_error_message}.")
            return str(ctx_error_message)

        cls.get_model(article_name=validated_data.article)

        async_session = await cls._get_connect()
        async with async_session as session:
            records = await cls._repository.get_last_hundred_records(
                session=session,
                tg_id=tg_id,
                model=cls._model,
            )
            cls.log.info(f"Метод get_expenses. Получены записи: {len(records)}.")
            return cls.make_a_dict(records=records)
