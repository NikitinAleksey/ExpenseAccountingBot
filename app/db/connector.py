from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

__all__ = [
    'PostgresConnector'
]


class PostgresConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PostgresConnector, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.postgres_user = settings.POSTGRES_USER
        self.postgres_password = settings.POSTGRES_PASSWORD.get_secret_value()
        self.postgres_db_name = settings.POSTGRES_DB_NAME
        self.postgres_host = settings.POSTGRES_HOST
        self.postgres_port = settings.POSTGRES_PORT
        self.echo = settings.DEBUG
        self.pool_size = settings.POOL_SIZE
        self.max_overflow = settings.MAX_OVERFLOW
        self.db_url = self.url_builder()
        self.engine = self.create_engine()
        self.async_session = self.create_session()

    def url_builder(self):
        return (
            f'postgresql+asyncpg://'
            f'{self.postgres_user}:'
            f'{self.postgres_password}@'
            f'{self.postgres_host}:'
            f'{self.postgres_port}/'
            f'{self.postgres_db_name}'
        )

    def create_engine(self):
        return create_async_engine(
            self.db_url,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow
        )

    def create_session(self):
        return sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def close(self):
        if self.engine:
            self.engine.dispose()

    # async def __aenter__(self):
    #     self.session = self.async_session()
    #     return self.session
    #
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     if self.session:
    #         await self.session.close()
