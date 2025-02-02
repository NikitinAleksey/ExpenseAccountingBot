from typing import Union

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.controller.user_controller import UserController
from app.api.servises.fsm.states import StatisticStates, TimezoneStates
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard

__all__ = ["commands_router", "start_handler"]

commands_router = Router()


@commands_router.callback_query(F.data == "start")
@commands_router.message(CommandStart())
async def start_handler(
    event: Union[Message, CallbackQuery], state: FSMContext, texts: dict
):
    """
    Обработчик команды /start.

    :param event: Сообщение или CallbackQuery.
    :param state: Контекст состояния FSM.
    :param texts: Словарь с текстами для ответа.
    :return: Ответное сообщение.
    """
    message = event.message if isinstance(event, CallbackQuery) else event
    await state.clear()
    return await message.answer(
        text=texts["commands"]["start"],
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["start"]
        ),
    )


@commands_router.callback_query(F.data == "statistic")
@commands_router.message(Command("statistic"))
async def statistic_handler(
    event: Union[Message, CallbackQuery], state: FSMContext, texts: dict
):
    """
    Обработчик команды /statistic.

    :param event: Сообщение или CallbackQuery.
    :param state: Контекст состояния FSM.
    :param texts: Словарь с текстами для ответа.
    :return: Ответное сообщение.
    """
    await state.clear()
    user = await UserController.get_user(tg_id=event.from_user.id)
    message = event.message if isinstance(event, CallbackQuery) else event

    if not user:
        return await message.answer(
            text=texts["statistic_texts"]["user_not_found"],
            reply_markup=InlineKeyBoard.create_kb(
                buttons=texts["inline_buttons"]["not_registered_yet"]
            ),
        )

    await state.set_data({"user": user})
    statistic_message = texts["commands"]["statistic"]
    await state.set_state(StatisticStates.waiting_for_report_type)
    return await message.answer(
        text=statistic_message,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["statistic"]["report_type"]
        ),
    )


@commands_router.callback_query(F.data == "register")
@commands_router.message(Command("register"))
async def register_handler(
    event: Union[Message, CallbackQuery], state: FSMContext, texts: dict
):
    """
    Обработчик команды /register.

    :param event: Сообщение или CallbackQuery.
    :param state: Контекст состояния FSM.
    :param texts: Словарь с текстами для ответа.
    :return: Ответное сообщение.
    """
    message = event.message if isinstance(event, CallbackQuery) else event
    register_message = texts["commands"]["register"]
    await state.set_state(TimezoneStates.waiting_for_add_timezone)
    return await message.answer(
        text=register_message,
        reply_markup=ReplyKeyBoard().create_kb(
            buttons=texts["reply_buttons"]["timezones"]
        ),
    )


@commands_router.message(Command("help"))
async def help_handler(message: Message, texts: dict):
    """
    Обработчик команды /help.

    :param message: Сообщение от пользователя.
    :param texts: Словарь с текстами для ответа.
    :return: Ответное сообщение.
    """
    help_message = texts["commands"]["help"]
    return await message.answer(text=help_message)
