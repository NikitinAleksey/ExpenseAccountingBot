from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.fsm.states import TimezoneStates
from app.api.routers.commands_router import start_handler
from app.api.controller.user_controller import UserController
from app.api.controller.limits_controller import LimitsController
from app.api.servises.timezone.timezone_service import parse_timezone

__all__ = ['register_router']

register_router = Router()


@register_router.message(StateFilter(TimezoneStates.waiting_for_add_timezone))
async def choose_timezone_handler(message: Message, state: FSMContext, texts: dict):
    try:
        timezone = parse_timezone(message=message.text)
    except ValueError as exc:
        return await message.answer(
            text=exc.__repr__(),
            reply_markup=ReplyKeyBoard().create_kb(texts["reply_buttons"]["timezones"])
        )

    is_success = await UserController.register_user(
        tg_id=message.from_user.id,
        name=message.from_user.full_name,
        timezone=timezone
    )
    await LimitsController.init_limits(
        tg_id=message.from_user.id
    )
    if is_success:
        timezone_message = texts["register_texts"]["done"]
    else:
        timezone_message = texts["register_texts"]["already_done"]
    await state.clear()
    return await message.answer(
        text=timezone_message,
        reply_markup=InlineKeyBoard().create_kb(texts["inline_buttons"]["ok"])
    )


@register_router.callback_query(F.data == 'change_timezone')
async def choose_new_timezone_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    timezone_message = texts["commands"]["register"]
    await state.set_state(TimezoneStates.waiting_for_change_timezone)
    return await callback.message.answer(
        text=timezone_message,
        reply_markup=ReplyKeyBoard().create_kb(texts["reply_buttons"]["timezones"])
    )


@register_router.message(StateFilter(TimezoneStates.waiting_for_change_timezone))
async def change_user_timezone_handler(message: Message, state: FSMContext, texts: dict):
    try:
        timezone = parse_timezone(message=message.text)
    except ValueError as exc:
        return await message.answer(
            text=str(exc),
            reply_markup=ReplyKeyBoard().create_kb(texts["reply_buttons"]["timezones"])
        )
    if await UserController.update_user(
            tg_id=message.from_user.id,
            name=message.from_user.full_name,
            timezone=timezone
    ):
        timezone_message = texts["timezone_texts"]["done"].format(timezone=message.text)
    else:
        timezone_message = texts["timezone_texts"]["error"]
    await state.clear()
    return await message.answer(
        text=timezone_message,
        reply_markup=InlineKeyBoard().create_kb(texts["inline_buttons"]["ok"])
    )