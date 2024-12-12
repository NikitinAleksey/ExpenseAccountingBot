from collections import OrderedDict
from datetime import datetime, timedelta

import pydantic

from app.db.connector import PostgresConnector
from app.db import Base
from app.db.repositories.expense_articles import ExpenseArticleRepository
from app.api.servises.mapping.mapping import ExpenseArticleMapping
from app.api.servises.validators.validators import InsertValidator, DeleteValidator, ArticleValidator
from app.db.models import BaseArticle


class ExpensesController:
    _connector = PostgresConnector()
    _repository = ExpenseArticleRepository
    _model = None

    @classmethod
    async def get_connect(cls):
        return cls._connector.async_session

    @classmethod
    def get_model(cls, article_name: str):
        cls._model = ExpenseArticleMapping.get_class_from_article_name(article_name=article_name)

    @classmethod
    def make_a_dict(cls, records: list[BaseArticle]):
        if not records:
            return
        formatted_records = OrderedDict()
        user_timezone = records[0].user.timezone
        for record in records:
            dt_with_offset = record.updated_at + timedelta(hours=user_timezone)
            formatted_time_with_offset = dt_with_offset.strftime("%d.%m.%Y %H:%M")
            formatted_records[record] = f'Сумма: {record.summ}\nДата: {formatted_time_with_offset}'
        return formatted_records

    @classmethod
    def extract_article_id_from_dict(cls, articles_dict: OrderedDict, article_value: str):
        for key in articles_dict.keys():
            if articles_dict[key] == article_value:
                return key
        return

    # @classmethod
    # def validate(cls, amount: str, article_name: str):
    #     validated_data = InsertValidator(amount=amount, article=article_name)
    #     return validated_data

    @classmethod
    async def add_expense(cls, tg_id: int, article_name: str, amount: str):
        try:
            validated_data = InsertValidator(amount=amount, article=article_name)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            return str(ctx_error_message)

        cls.get_model(article_name=validated_data.article)

        async_session = await cls.get_connect()
        async with async_session() as session:
            new_expense_model = cls._model(
                user_id=tg_id,
                summ=validated_data.amount
            )
            record = await cls._repository.create(session=session, item=new_expense_model)
            return record

    @classmethod
    async def delete_expense(cls, articles_dict: OrderedDict, article_value: str):
        article = cls.extract_article_id_from_dict(articles_dict=articles_dict, article_value=article_value)
        if not article:
            return

        async_session = await cls.get_connect()
        async with async_session() as session:
            delete_item = await ExpenseArticleRepository.delete(session=session, item=article)
            return delete_item

    @classmethod
    async def get_expenses(cls, tg_id: int, article_name: str):
        try:
            validated_data = ArticleValidator(article=article_name)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            return str(ctx_error_message)

        cls.get_model(article_name=validated_data.article)

        async_session = await cls.get_connect()
        async with async_session() as session:
            records = await cls._repository.get_last_hundred_records(
                session=session,
                tg_id=tg_id,
                model=cls._model,
            )
            return cls.make_a_dict(records=records)

