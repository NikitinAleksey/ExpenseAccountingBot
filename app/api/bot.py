from typing import Any, List, Type

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

__all__ = ["create_bot"]


async def register_all_routers(dp: Dispatcher, routers: List[Router]):
    """
    Регистрирует все роутеры в диспетчере.

    :param dp: Dispatcher - объект диспетчера для регистрации роутеров.
    :param routers: List[Router] - список роутеров для регистрации.
    :return: None
    """
    for router in routers:
        dp.include_router(router=router)


async def register_all_middleware(
    dp: Dispatcher, middlewares: List[BaseMiddleware], data: Any
):
    """
    Регистрирует все миддлвары в диспетчере.

    :param dp: Dispatcher - объект диспетчера для регистрации миддлваров.
    :param middlewares: List[BaseMiddleware] - список миддлваров для регистрации.
    :param data: Any - дополнительные данные, передаваемые миддлварам.
    :return: None
    """
    for middleware in middlewares:
        dp.update.middleware(middleware(data))


async def create_bot(
    token: str, routers: List[Router], middlewares: List[BaseMiddleware], texts: dict
):
    """
    Создает экземпляры бота и диспетчера с зарегистрированными роутерами и миддлварами.

    :param token: str - токен для бота.
    :param routers: List[Router] - список роутеров для регистрации.
    :param middlewares: List[BaseMiddleware] - список миддлваров для регистрации.
    :param texts: dict - словарь с текстами для миддлваров.
    :return: Tuple[Bot, Dispatcher] - объекты бота и диспетчера.
    """
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await register_all_routers(dp=dp, routers=routers)
    await register_all_middleware(dp=dp, middlewares=middlewares, data=texts)
    return bot, dp
