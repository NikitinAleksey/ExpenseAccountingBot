from app.api.controller import BaseController
from app.db.connector import PostgresConnector
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.utils import logged

__all__ = ["UserController"]


@logged()
class UserController(BaseController):
    _repository = UserRepository
    _user = User

    @classmethod
    async def register_user(cls, tg_id: int, name: str, timezone: int):
        """
        Регистрация нового пользователя в системе.

        :param tg_id: ID пользователя в Telegram.
        :param name: Имя пользователя.
        :param timezone: Часовой пояс пользователя.
        :return: Зарегистрированный пользователь.
        """
        cls.log.info(
            f"Метод register_user. Попытка регистрации пользователя tg_id={tg_id}, "
            f"name={name}, timezone={timezone}."
        )
        async_session = await cls._get_connect()
        cls.log.debug("Метод register_user. Соединение получено.")
        async with async_session as session:
            user = await cls._repository.read(
                session=session, tg_id=tg_id, model=cls._user
            )
            cls.log.debug(
                f"Метод register_user. Проверка наличия пользователя с tg_id={tg_id}."
            )
            if user:
                cls.log.info(
                    f"Метод register_user. Пользователь с {tg_id=} уже зарегистрирован."
                )
                return
            new_user = cls._user(tg_id=tg_id, name=name, timezone=timezone)
            cls.log.debug(f"Метод register_user. Новый пользователь: {new_user}.")

            user = await cls._repository.create(session=session, item=new_user)
            cls.log.info(
                f"Метод register_user. Пользователь с {tg_id=} успешно зарегистрирован."
            )

            return user

    @classmethod
    async def update_user(cls, tg_id: int, name: str, timezone: int):
        """
        Обновление данных пользователя.

        :param tg_id: ID пользователя.
        :param name: Новое имя пользователя.
        :param timezone: Новый часовой пояс пользователя.
        :return: Обновленные данные пользователя.
        """
        cls.log.info(f"Метод update_user. Обновление данных пользователя {tg_id=}.")
        async_session = await cls._get_connect()
        async with async_session as session:
            updated_user = cls._user(tg_id=tg_id, name=name, timezone=timezone)
            cls.log.debug(
                f"Метод update_user. Новый данные пользователя: {updated_user}."
            )

            await cls._repository.update(session=session, item=updated_user)
            cls.log.info(
                f"Метод update_user. Данные пользователя {tg_id=} успешно обновлены."
            )
            return updated_user

    @classmethod
    async def get_user(cls, tg_id: int):
        """
        Поиск пользователя по его tg_id.

        :param tg_id: ID пользователя в Telegram.
        :return: Найденный пользователь или None, если пользователь не найден.
        """
        cls.log.info(f"Метод get_user. Поиск пользователя с {tg_id=}.")
        async_session = await cls._get_connect()
        async with async_session as session:
            user = await cls._repository.read(
                session=session, tg_id=tg_id, model=cls._user
            )
        if not user:
            cls.log.warning(f"Метод get_user. Пользователь с {tg_id=} не найден.")
        return user
