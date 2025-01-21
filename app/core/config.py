import os

import pydantic
import pydantic_settings

__all__ = ["settings"]


class Settings(pydantic_settings.BaseSettings):
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
