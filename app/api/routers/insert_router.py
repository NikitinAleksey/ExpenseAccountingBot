from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.controller.expenses_controller import ExpensesController
from app.api.routers.commands_router import start_handler
from app.api.servises.fsm.states import InsertStates
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard

__all__ = ["insert_router"]

insert_router = Router()


@insert_router.callback_query(F.data == "insert")
async def insert_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    """
    Обработка запроса на добавление расходной статьи.

    :param callback: CallbackQuery, содержащий данные запроса.
    :param state: FSMContext, контекст состояния.
    :param texts: Словарь с текстами для сообщений.
    :return: Отправка сообщения с запросом статьи расхода.
    """
    insert_message = texts["insert_texts"]["item"]
    await state.set_state(InsertStates.waiting_for_insert_item)
    return await callback.message.answer(
        text=insert_message,
        reply_markup=ReplyKeyBoard().create_kb(
            buttons=texts["reply_buttons"]["expense_item"]
        ),
    )


@insert_router.message(StateFilter(InsertStates.waiting_for_insert_item))
async def insert_waiting_for_item(message: Message, state: FSMContext, texts: dict):
    """
    Ожидание ввода статьи расхода от пользователя.

    :param message: Сообщение пользователя с введенным текстом.
    :param state: FSMContext, контекст состояния.
    :param texts: Словарь с текстами для сообщений.
    :return: Отправка сообщения с запросом суммы расхода.
    """
    formatted_msg = texts["insert_texts"]["sum"].format(item=message.text)
    await state.set_data({"expense_article": message.text})
    await state.set_state(InsertStates.waiting_for_insert_sum)
    return await message.reply(
        text=formatted_msg,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["back_to_main"]
        ),
    )


@insert_router.message(StateFilter(InsertStates.waiting_for_insert_sum))
async def insert_waiting_for_sum(message: Message, state: FSMContext, texts: dict):
    """
    Ожидание ввода суммы расхода от пользователя.

    :param message: Сообщение пользователя с введенной суммой.
    :param state: FSMContext, контекст состояния.
    :param texts: Словарь с текстами для сообщений.
    :return: Подтверждение добавления расхода и запрос на повторение.
    """
    state_data = await state.get_data()
    expense_article = state_data.get("expense_article")
    record = await ExpensesController.add_expense(
        tg_id=message.from_user.id, article_name=expense_article, amount=message.text
    )
    if isinstance(record, str):
        await state.set_state(InsertStates.waiting_for_insert_item)
        return await message.answer(
            text=record,
            reply_markup=ReplyKeyBoard().create_kb(
                buttons=texts["reply_buttons"]["expense_item"]
            ),
        )

    formatted_msg = texts["insert_texts"]["done"].format(sum=record.summ)
    await state.set_state(InsertStates.waiting_for_repeat_insert)
    return await message.reply(
        text=formatted_msg,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["insert_yes_no"]
        ),
    )


@insert_router.callback_query(StateFilter(InsertStates.waiting_for_repeat_insert))
async def insert_waiting_for_repeat(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обработка запроса на повторное добавление расхода.

    :param callback: CallbackQuery, содержащий данные запроса.
    :param state: FSMContext, контекст состояния.
    :param texts: Словарь с текстами для сообщений.
    :return: Перевод в соответствующее состояние или завершение.
    """
    if callback.message.text == "Да":
        await state.set_state(InsertStates.waiting_for_insert_item)
        return await insert_handler(callback=callback, state=state, texts=texts)
    else:
        await state.clear()
        return await start_handler(message=callback.message, state=state, texts=texts)
