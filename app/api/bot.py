from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey
from aiogram import Router, BaseMiddleware


__all__ = ["create_bot"]


async def register_all_routers(dp: Dispatcher, routers: list[Router]):
    for router in routers:
        dp.include_router(router=router)


async def register_all_middleware(
    dp: Dispatcher, middlewares: list[BaseMiddleware], data: Any
):
    for middleware in middlewares:
        dp.update.middleware(middleware(data))


async def create_bot(
    token: str, routers: list[Router], middlewares: list[BaseMiddleware], texts: dict
):
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await register_all_routers(dp=dp, routers=routers)
    await register_all_middleware(dp=dp, middlewares=middlewares, data=texts)
    return bot, dp
