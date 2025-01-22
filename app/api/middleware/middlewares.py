import asyncio
from typing import Any, Awaitable, Callable, Dict
from unittest.mock import _SentinelObject

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.storage.base import BaseStorage
from aiogram.types import Message, TelegramObject

from app.utils import logged

__all__ = ["StorageMiddleware", "DeletePreviousMSGMiddleware"]


class StorageMiddleware(BaseMiddleware):
    """
    Миддлвар для работы с хранилищем.

    :param storage: Хранилище для данных.
    """

    def __init__(self, storage: BaseStorage):
        super().__init__()
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обработка события и передача данных в хранилище.

        :param handler: Обработчик события.
        :param event: Событие Telegram.
        :param data: Данные, передаваемые в обработчик.
        :return: Результат выполнения обработчика.
        """
        data["texts"] = self.storage
        result = await handler(event, data)
        return result


@logged()
class DeletePreviousMSGMiddleware(BaseMiddleware):
    """
    Миддлвар для удаления предыдущих сообщений в чате.

    :param storage: Хранилище для хранения сообщений.
    """

    def __init__(self, storage: BaseStorage):
        super().__init__()
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Удаление предыдущих сообщений и передача события.

        :param handler: Обработчик события.
        :param event: Событие Telegram.
        :param data: Данные, передаваемые в обработчик.
        :return: Результат выполнения обработчика.
        """
        chat_id = (
            event.message.chat.id
            if event.message
            else event.callback_query.message.chat.id
        )
        if self.storage.get(chat_id):
            while not self.storage[chat_id].empty():
                event_to_be_cleaned = await self.storage[chat_id].get()
                try:
                    await event_to_be_cleaned.delete()
                except AttributeError as exc:
                    self.log.warning(f"Чат: {chat_id}. Ошибка: {exc}.")
        else:
            self.storage[chat_id] = asyncio.Queue()

        if isinstance(event.message, Message):
            await self.storage[chat_id].put(event.message)

        result = await handler(event, data)

        if not isinstance(result, _SentinelObject):
            await self.storage[chat_id].put(result)
        return result
