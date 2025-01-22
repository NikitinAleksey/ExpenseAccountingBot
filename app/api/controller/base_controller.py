from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.connector import PostgresConnector

__all__ = ["BaseController"]


class BaseController:
    _connector = PostgresConnector()

    @classmethod
    async def _get_connect(cls) -> sessionmaker[AsyncSession]:
        """
        Получает объект сессии из пула коннектора.

        :return: Объект сессии для работы с базой данных.
        """
        async with cls._connector.get_session() as session:
            return session
