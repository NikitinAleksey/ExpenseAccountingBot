from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.controller.limits_controller import LimitsController
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.fsm.states import LimitsStates
from app.api.routers.commands_router import start_handler


__all__ = ["limits_router"]


limits_router = Router()


@limits_router.callback_query(F.data == "limits")
async def limits_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    limits_message = texts["limits_texts"]["item"]
    await state.set_state(LimitsStates.waiting_for_limits_item)
    return await callback.message.answer(
        text=limits_message,
        reply_markup=ReplyKeyBoard().create_kb(
            buttons=texts["reply_buttons"]["expense_item"]
        ),
    )


@limits_router.message(StateFilter(LimitsStates.waiting_for_limits_item))
async def limits_waiting_for_item(message: Message, state: FSMContext, texts: dict):
    limits_sum_message = texts["limits_texts"]["sum"].format(item=message.text)
    await state.set_state(LimitsStates.waiting_for_limits_sum)
    await state.set_data({"article_name_to_update": message.text})
    return await message.reply(
        text=limits_sum_message,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["back_to_main"]
        ),
    )


@limits_router.message(StateFilter(LimitsStates.waiting_for_limits_sum))
async def limits_waiting_for_sum(message: Message, state: FSMContext, texts: dict):
    # TODO написать вызов класса, который будет записывать лимиты в бд + валидацию пройти через InsertValidator
    data = await state.get_data()
    updated_record = await LimitsController.update_limit(
        tg_id=message.from_user.id,
        article_name=data.get("article_name_to_update"),
        article_value=message.text,
    )

    if isinstance(updated_record, str):
        await state.set_state(LimitsStates.waiting_for_limits_item)
        return await message.reply(
            text=updated_record,
            reply_markup=ReplyKeyBoard().create_kb(
                buttons=texts["reply_buttons"]["expense_item"]
            ),
        )

    formatted_msg = texts["limits_texts"]["done"].format(sum=message.text)
    await state.set_state(LimitsStates.waiting_for_repeat_limits)
    return await message.reply(
        text=formatted_msg,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["limits_yes_no"]
        ),
    )


@limits_router.callback_query(StateFilter(LimitsStates.waiting_for_repeat_limits))
async def limits_waiting_for_repeat(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    if callback.message.text == "Да":
        await state.set_state(LimitsStates.waiting_for_limits_item)
        return await limits_handler(callback=callback, state=state, texts=texts)
    else:
        await state.clear()
        return await start_handler(message=callback.message, state=state, texts=texts)
