from app.db.connector import PostgresConnector
from app.utils import logged


__all__ = ['BaseController']


class BaseController:
    _connector = PostgresConnector()

    @classmethod
    async def _get_connect(cls):
        async with cls._connector.get_session() as session:
            return session
