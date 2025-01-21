import asyncio
import functools
from typing import Callable, Dict, Any, Awaitable
from unittest.mock import _SentinelObject

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from app.utils import logged


__all__ = ["StorageMiddleware", "DeletePreviousMSGMiddleware"]


class StorageMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage):
        super().__init__()
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["texts"] = self.storage
        result = await handler(event, data)
        return result


@logged()
class DeletePreviousMSGMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage):
        super().__init__()
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat_id = (
            event.message.chat.id
            if event.message
            else event.callback_query.message.chat.id
        )
        self.log.info(f"Чат: {chat_id}. Получили чат id.")
        if self.storage.get(chat_id):
            while not self.storage[chat_id].empty():
                event_to_be_cleaned = await self.storage[chat_id].get()
                try:
                    await event_to_be_cleaned.delete()
                except AttributeError as exc:
                    # TODO логгер, конечно
                    print(exc)
            self.log.info(f"Чат: {chat_id}. Удалили старые сообщения.")
        else:
            self.storage[chat_id] = asyncio.Queue()
            self.log.info(
                f"Чат: {chat_id}. Чат пуст, создали очередь для сообщений, которые будут удалены."
            )
        if isinstance(event.message, Message):
            await self.storage[chat_id].put(event.message)
            self.log.info(
                f"Чат: {chat_id}. Входящее событие - сообщение. Добавили в очередь."
            )
        result = await handler(event, data)

        if not isinstance(result, _SentinelObject):
            await self.storage[chat_id].put(result)
        self.log.info(f"Чат: {chat_id}. Ответили пользователю.")
        return result
