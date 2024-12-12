from app.db.models.user import User
from app.db.connector import PostgresConnector
from app.db.repositories.user import UserRepository


__all__ = ['UserController']


class UserController:
    _connector = PostgresConnector()
    _repository = UserRepository
    _user = User

    @classmethod
    async def get_connect(cls):
        return cls._connector.async_session

    @classmethod
    async def register_user(cls, tg_id: int, name: str, timezone: int):
        async_session = await cls.get_connect()
        async with async_session() as session:
            user = await cls._repository.read(session=session, tg_id=tg_id, model=cls._user)
            if user:
                # self.user = user
                return False
            new_user = cls._user(
                tg_id=tg_id,
                name=name,
                timezone=timezone
            )
            user = await cls._repository.create(session=session, item=new_user)
            # self.user = user
        return True

    @classmethod
    async def update_user(cls, tg_id: int, name: str, timezone: int):
        async_session = await cls.get_connect()
        async with async_session() as session:
            updated_user = cls._user(
                tg_id=tg_id,
                name=name,
                timezone=timezone
            )
            await cls._repository.update(
                session=session,
                item=updated_user
            )
            return updated_user
