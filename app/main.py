import asyncio

from api.bot import create_bot
from api.middleware.middlewares import (DeletePreviousMSGMiddleware,
                                        StorageMiddleware)
from api.routers.commands_router import commands_router
from api.routers.delete_router import delete_router
from api.routers.insert_router import insert_router
from api.routers.limits_router import limits_router
from api.routers.register_router import register_router
from api.routers.statistic_router import statistic_router
from api.servises.texts.texts import texts
from core.config import settings

routers_list = [
    commands_router,
    statistic_router,
    insert_router,
    delete_router,
    limits_router,
    register_router,
]

middlewares = [StorageMiddleware, DeletePreviousMSGMiddleware]


async def start_bot(token: str):
    """
    Запускает бота с указанными параметрами.

    :param token: str - токен для подключения бота.
    :return: запускает процесс polling для бота.
    """
    bot, dp = await create_bot(
        token=token, routers=routers_list, middlewares=middlewares, texts=texts
    )
    await dp.start_polling(bot)


async def create_app():
    """
    Создает и запускает приложение.

    :return: запускает асинхронную задачу для старта бота.
    """
    bot_task = asyncio.create_task(start_bot(settings.TG_BOT_TOKEN.get_secret_value()))
    await bot_task


if __name__ == "__main__":
    asyncio.run(create_app())
