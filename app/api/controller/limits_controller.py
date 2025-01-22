import pydantic

from app.api.controller import BaseController
from app.api.servises.validators.validators import LimitsValidator
from app.db.models import MonthlyLimits
from app.db.repositories.monthly_limits import LimitsRepository
from app.utils import logged

__all__ = ["LimitsController"]


@logged()
class LimitsController(BaseController):
    """Контроллер для управления месячными лимитами пользователей."""
    _repository = LimitsRepository
    _model = MonthlyLimits

    @classmethod
    async def init_limits(cls, tg_id: int) -> MonthlyLimits:
        """
        Инициализирует лимиты для указанного пользователя.

        :param tg_id: ID пользователя в Telegram.
        :return: Созданная запись с лимитами.
        """
        cls.log.info(f"Метод init_limits. Инициализация лимитов для {tg_id=}.")
        async_session = await cls._get_connect()
        async with async_session as session:
            new_limits_model = cls._model(user_id=tg_id)
            record = await cls._repository.create(
                session=session, item=new_limits_model
            )
            cls.log.info(
                f"Метод init_limits. Лимиты успешно инициализированы для tg_id={tg_id}."
            )
            return record

    @classmethod
    async def update_limit(
        cls, tg_id: int, article_name: str, article_value: str
    ) -> MonthlyLimits | str:
        """
        Обновляет лимит для указанного пользователя по статье расходов.

        :param tg_id: ID пользователя в Telegram.
        :param article_name: Название статьи расходов.
        :param article_value: Новое значение лимита.
        :return: Обновленная запись с лимитом или сообщение об ошибке.
        """
        cls.log.info(
            f"Метод update_limit. Обновление лимита для tg_id={tg_id}, "
            f"article_name={article_name}, article_value={article_value}."
        )
        try:
            validated_data = LimitsValidator(amount=article_value, article=article_name)
            cls.log.info(
                f"Метод update_limit. Валидация успешна для: {validated_data.amount}."
            )
        except pydantic.ValidationError as exc:
            ctx_error_message = exc.errors()[0]["ctx"]["error"].args[0]
            cls.log.error(f"Метод update_limit. Ошибка валидации: {ctx_error_message}.")
            return str(ctx_error_message)

        async_session = await cls._get_connect()
        async with async_session as session:
            current_record = await cls._repository.read(
                session=session, tg_id=tg_id, model=cls._model
            )
            cls.log.info(
                f"Метод update_limit. Текущий лимит для tg_id={tg_id}: {current_record}."
            )
            setattr(current_record, validated_data.article, validated_data.amount)
            updated_record = await cls._repository.update(
                session=session, item=current_record
            )
            cls.log.info(
                f"Метод update_limit. Лимит обновлен для tg_id={tg_id}: {updated_record}."
            )
            return updated_record
