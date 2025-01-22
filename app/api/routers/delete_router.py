from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.controller.expenses_controller import ExpensesController
from app.api.routers.commands_router import start_handler
from app.api.servises.fsm.states import DeleteStates
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard

__all__ = ["delete_router"]

delete_router = Router()


@delete_router.callback_query(F.data == "delete")
async def delete_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    """
    Обрабатывает запрос на удаление и выводит сообщение для выбора статьи расходов.

    :param callback: Callback-запрос от пользователя.
    :param state: Состояние FSM.
    :param texts: Словарь с текстами для ответов.
    :return: Ответ с текстом и кнопками для выбора статьи расходов.
    """
    delete_message = texts["delete_texts"]["item"]
    await state.set_state(DeleteStates.waiting_for_chose_article)
    return await callback.message.answer(
        text=delete_message,
        reply_markup=ReplyKeyBoard().create_kb(
            buttons=texts["reply_buttons"]["expense_item"]
        ),
    )


@delete_router.message(StateFilter(DeleteStates.waiting_for_chose_article))
async def delete_waiting_for_chose_item(
    message: Message, state: FSMContext, texts: dict
):
    """
    Ожидает выбора статьи для удаления и выводит список записей.

    :param message: Сообщение пользователя с выбранной статьей.
    :param state: Состояние FSM.
    :param texts: Словарь с текстами для ответов.
    :return: Ответ с найденными записями или сообщением об ошибке.
    """
    records = await ExpensesController.get_expenses(
        tg_id=message.from_user.id, article_name=message.text
    )
    if not records:
        empty_message = texts["delete_texts"]["empty"].format(article=message.text)
        await state.clear()
        await message.answer(
            text=empty_message,
            reply_markup=InlineKeyBoard.create_kb(
                buttons=texts["inline_buttons"]["ok"]
            ),
        )

    if isinstance(records, str):
        return await message.answer(
            text=records,
            reply_markup=ReplyKeyBoard().create_kb(
                buttons=texts["reply_buttons"]["expense_item"]
            ),
        )

    await state.set_state(DeleteStates.waiting_for_delete_article)
    await state.set_data({"articles_to_delete": records})

    formatted_msg = texts["delete_texts"]["article"].format(item=message.text)
    return await message.reply(
        text=formatted_msg, reply_markup=ReplyKeyBoard().create_kb(records.values())
    )


@delete_router.message(StateFilter(DeleteStates.waiting_for_delete_article))
async def delete_waiting_for_item(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает подтверждение удаления статьи расходов.

    :param message: Сообщение с подтверждением удаления.
    :param state: Состояние FSM.
    :param texts: Словарь с текстами для ответов.
    :return: Ответ с результатом удаления и кнопками для повторного удаления.
    """
    data = await state.get_data()
    delete_record = await ExpensesController.delete_expense(
        articles_dict=data.get("articles_to_delete"), article_value=message.text
    )
    if not delete_record:
        delete_message = texts["delete_texts"]["error"]
    else:
        delete_message = texts["delete_texts"]["done"]

    await state.set_state(DeleteStates.waiting_for_repeat_deletion)
    return await message.reply(
        text=delete_message,
        reply_markup=InlineKeyBoard().create_kb(
            buttons=texts["inline_buttons"]["delete_yes_no"]
        ),
    )


@delete_router.callback_query(StateFilter(DeleteStates.waiting_for_repeat_deletion))
async def delete_waiting_for_repeat(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Ожидает повторного подтверждения на удаление или возвращает к начальной команде.

    :param callback: Callback-запрос от пользователя.
    :param state: Состояние FSM.
    :param texts: Словарь с текстами для ответов.
    :return: Ответ с дальнейшими действиями в зависимости от выбора.
    """
    if callback.message.text == "Да":
        await state.set_state(DeleteStates.waiting_for_chose_article)
        return await delete_handler(callback=callback, state=state, texts=texts)
    else:
        await state.clear()
        return await start_handler(message=callback.message, state=state, texts=texts)
