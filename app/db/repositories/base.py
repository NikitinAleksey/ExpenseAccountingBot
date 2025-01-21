from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base


class BaseRepository(ABC):
    @abstractmethod
    async def create(self, session: AsyncSession, item: Base):
        pass

    @abstractmethod
    async def read(self, session: AsyncSession, tg_id: int, model: Base):
        pass

    @abstractmethod
    async def update(self, session: AsyncSession, item: Base):
        pass

    @abstractmethod
    async def delete(self, session: AsyncSession, item: Base):
        pass
