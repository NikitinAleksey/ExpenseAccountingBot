import os

import pydantic
import pydantic_settings

__all__ = ["settings"]


class Settings(pydantic_settings.BaseSettings):
    """
    Настройки для проекта, загружаемые из .env файла.

    :param TG_BOT_TOKEN: SecretStr - токен для бота Telegram.
    :param POSTGRES_USER: str - имя пользователя для подключения к базе данных PostgreSQL.
    :param POSTGRES_PASSWORD: SecretStr - пароль для подключения к базе данных PostgreSQL.
    :param POSTGRES_DB_NAME: str - имя базы данных PostgreSQL.
    :param POSTGRES_HOST: str - хост для подключения к базе данных PostgreSQL.
    :param POSTGRES_PORT: int - порт для подключения к базе данных PostgreSQL.
    :param POOL_SIZE: int - размер пула соединений для базы данных.
    :param MAX_OVERFLOW: int - максимальное количество дополнительных соединений.
    :param DEBUG: bool - флаг для режима отладки.
    :return: объект Settings с настройками проекта.
    """

    TG_BOT_TOKEN: pydantic.SecretStr

    POSTGRES_USER: str
    POSTGRES_PASSWORD: pydantic.SecretStr
    POSTGRES_DB_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    POOL_SIZE: int
    MAX_OVERFLOW: int

    DEBUG: bool

    class Config:
        env_file = os.path.abspath(os.path.join("..", ".env"))


settings = Settings()
