from collections import OrderedDict
from datetime import datetime, timedelta

import pydantic

from app.db.connector import PostgresConnector
from app.db import Base
from app.db.repositories.monthly_limits import LimitsRepository
from app.api.servises.mapping.mapping import ExpenseLimitsArticleMapping
from app.api.servises.validators.validators import LimitsValidator
from app.db.models import MonthlyLimits


__all__ = ['LimitsController']


class LimitsController:
    _connector = PostgresConnector()
    _repository = LimitsRepository
    _model = MonthlyLimits

    @classmethod
    async def get_connect(cls):
        return cls._connector.async_session

    @classmethod
    async def init_limits(cls, tg_id: int):
        async_session = await cls.get_connect()
        async with async_session() as session:
            new_limits_model = cls._model(
                user_id=tg_id
            )
            record = await cls._repository.create(session=session, item=new_limits_model)
            return record

    @classmethod
    async def update_limit(cls, tg_id: int, article_name: str, article_value: str):
        try:
            validated_data = LimitsValidator(amount=article_value, article=article_name)
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
            return str(ctx_error_message)

        async_session = await cls.get_connect()
        async with async_session() as session:
            current_record = await cls._repository.read(
                session=session,
                tg_id=tg_id,
                model=cls._model
            )
            setattr(current_record, validated_data.article, validated_data.amount)
            updated_record = await cls._repository.update(
                session=session,
                item=current_record
            )
            return updated_record


    # @classmethod
    # async def delete_expense(cls, articles_dict: OrderedDict, article_value: str):
    #     article = cls.extract_article_id_from_dict(articles_dict=articles_dict, article_value=article_value)
    #     if not article:
    #         return
    #
    #     async_session = await cls.get_connect()
    #     async with async_session() as session:
    #         delete_item = await ExpenseArticleRepository.delete(session=session, item=article)
    #         return delete_item
    #
    # @classmethod
    # async def get_expenses(cls, tg_id: int, article_name: str):
    #     try:
    #         validated_data = ArticleValidator(article=article_name)
    #     except pydantic.ValidationError as exc:
    #         ctx_error_message = exc.errors()[0]['ctx']['error'].args[0]
    #         return str(ctx_error_message)
    #
    #     cls.get_model(article_name=validated_data.expense_article)
    #
    #     async_session = await cls.get_connect()
    #     async with async_session() as session:
    #         records = await cls._repository.get_last_hundred_records(
    #             session=session,
    #             tg_id=tg_id,
    #             model=cls._model,
    #         )
    #         return cls.make_a_dict(records=records)

