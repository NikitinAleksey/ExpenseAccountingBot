from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.api.controller.statistic_controller import StatisticController
from app.api.servises.fsm.states import StatisticStates
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard

__all__ = ["statistic_router"]

statistic_router = Router()


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_report_type), F.data == "fast_report"
)
async def statistic_make_fast_report(
        callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает запрос на быстрый отчет, генерируя отчет по данным пользователя.

    :param callback: CallbackQuery - запрос от пользователя.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет отчет пользователю.
    """
    data = await state.get_data()
    user = data.get("user")

    controller = StatisticController(
        tg_id=callback.from_user.id,
        mapping=texts["mapping_rus_to_eng"],
        report_type="fast",
        user=user,
    )
    report = await controller.get_report()
    await state.set_data({})
    return await callback.message.answer(
        text=f"```{report}```",
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyBoard.create_kb(buttons=texts["inline_buttons"]["ok"]),
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_report_type),
    F.data == "parametrized_report",
)
async def statistic_parametrized_report(
        callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает запрос на параметризированный отчет, переходя к выбору периода.

    :param callback: CallbackQuery - запрос от пользователя.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор периода.
    """
    await state.set_state(StatisticStates.parametrized_start_period_years)
    return await callback.message.answer(
        text=texts["statistic_texts"]["period_type"],
        reply_markup=InlineKeyBoard.create_kb(
            buttons=texts["inline_buttons"]["statistic"]["period_type"], adjust=3
        ),
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.parametrized_start_period_years)
)
async def statistic_start_year_handler(
        callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает выбор года для параметризированного отчета.

    :param callback: CallbackQuery - запрос от пользователя.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор месяцев для указанного года.
    """
    data = await state.get_data()
    user = data.get("user")

    controller = StatisticController(
        tg_id=callback.from_user.id,
        mapping=texts["mapping_eng_to_rus"],
        template=texts["parametrized_report_template"],
        report_type="parametrized",
        user=user,
    )
    controller.target_state = getattr(StatisticStates, callback.data)
    await state.set_data({"controller": controller})

    if controller.target_state == StatisticStates.parametrized_end_period_years:
        await state.set_state(StatisticStates.parametrized_end_period_years)
    else:
        await state.set_state(StatisticStates.parametrized_start_period_months)

    return await callback.message.answer(
        text=texts["statistic_texts"]["years"]["start"],
        reply_markup=ReplyKeyBoard.create_kb(buttons=controller.year_builder()),
    )


@statistic_router.message(StateFilter(StatisticStates.parametrized_start_period_months))
async def statistic_start_month_handler(
        message: Message, state: FSMContext, texts: dict
):
    """
    Обрабатывает выбор месяца для параметризированного отчета.

    :param message: Message - сообщение пользователя с выбранным месяцем.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор дней для указанного месяца.
    """
    data = await state.get_data()
    controller = data.get("controller")

    validated_year = controller.set_year(year=message.text, edge="start")
    if isinstance(validated_year, str):
        return await message.answer(
            text=validated_year,
            reply_markup=ReplyKeyBoard.create_kb(buttons=controller.year_builder()),
        )

    if controller.target_state == StatisticStates.parametrized_end_period_months:
        await state.set_state(StatisticStates.parametrized_end_period_years)
    else:
        await state.set_state(StatisticStates.parametrized_start_period_days)

    return await message.answer(
        text=texts["statistic_texts"]["months"]["start"].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=texts["reply_buttons"]["months"]),
    )


@statistic_router.message(StatisticStates.parametrized_start_period_days)
async def statistic_start_day_handler(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает выбор дня для параметризированного отчета.

    :param message: Message - сообщение пользователя с выбранным днем.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор даты для указанного дня.
    """
    data = await state.get_data()
    controller = data.get("controller")

    validated_month = controller.set_month(month=message.text, edge="start")
    if isinstance(validated_month, str):
        return await message.answer(
            text=validated_month,
            reply_markup=ReplyKeyBoard.create_kb(
                buttons=texts["reply_buttons"]["months"]
            ),
        )

    await state.set_state(StatisticStates.parametrized_end_period_years)
    days_buttons = controller.day_builder(date=controller.start)
    return await message.answer(
        text=texts["statistic_texts"]["days"]["start"].format(month=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=days_buttons),
    )


@statistic_router.message(StatisticStates.parametrized_end_period_years)
async def statistic_end_year_handler(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает выбор года для окончания периода параметризированного отчета.

    :param message: Message - сообщение пользователя с выбранным годом.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор месяца для окончания периода.
    """
    data = await state.get_data()
    controller = data.get("controller")

    if controller.target_state == StatisticStates.parametrized_end_period_years:
        possible_error = controller.set_year(year=message.text, edge="start")
        kb = ReplyKeyBoard.create_kb(buttons=controller.year_builder())
        await state.set_state(StatisticStates.got_dates)

    else:
        await state.set_state(StatisticStates.parametrized_end_period_months)
        if controller.target_state == StatisticStates.parametrized_end_period_days:
            possible_error = controller.set_day(
                day=message.text,
                month=controller.start.month,
                year=controller.start.year,
                edge="start",
            )
            kb = ReplyKeyBoard.create_kb(controller.day_builder(date=controller.start))

        else:
            possible_error = controller.set_month(month=message.text, edge="start")
            kb = ReplyKeyBoard.create_kb(buttons=texts["reply_buttons"]["months"])

    if possible_error:
        await state.set_state(StatisticStates.parametrized_end_period_years)
        return await message.answer(text=possible_error, reply_markup=kb)
    return await message.answer(
        text=texts["statistic_texts"]["years"]["end"].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=controller.year_builder()),
    )


@statistic_router.message(StateFilter(StatisticStates.parametrized_end_period_months))
async def statistic_end_month_handler(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает выбор месяца для окончания периода параметризированного отчета.

    :param message: Message - сообщение пользователя с выбранным месяцем.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор дня для окончания периода.
    """
    data = await state.get_data()
    controller = data.get("controller")
    validated_year = controller.set_year(year=message.text, edge="end")

    if isinstance(validated_year, str):
        return await message.answer(
            text=validated_year,
            reply_markup=ReplyKeyBoard.create_kb(buttons=controller.year_builder()),
        )

    if controller.target_state == StatisticStates.parametrized_end_period_months:
        await state.set_state(StatisticStates.got_dates)
    else:
        await state.set_state(StatisticStates.parametrized_end_period_days)

    return await message.answer(
        text=texts["statistic_texts"]["months"]["end"].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=texts["reply_buttons"]["months"]),
    )


@statistic_router.message(StatisticStates.parametrized_end_period_days)
async def statistic_end_day_handler(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает выбор дня для окончания периода параметризированного отчета.

    :param message: Message - сообщение пользователя с выбранным днем.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на завершение выбора данных для отчетности.
    """
    data = await state.get_data()
    controller = data.get("controller")
    validated_month = controller.set_month(month=message.text, edge="end")

    if isinstance(validated_month, str):
        return await message.answer(
            text=validated_month,
            reply_markup=ReplyKeyBoard.create_kb(
                buttons=texts["reply_buttons"]["months"]
            ),
        )

    await state.set_state(StatisticStates.got_dates)
    days_buttons = controller.day_builder(date=controller.end)
    return await message.answer(
        text=texts["statistic_texts"]["days"]["end"].format(month=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=days_buttons),
    )


@statistic_router.message(StatisticStates.got_dates)
async def statistic_got_dates_handler(message: Message, state: FSMContext, texts: dict):
    """
    Обрабатывает полученные даты для формирования отчетности.

    :param message: Message - сообщение пользователя с выбранной датой.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор типа группировки данных.
    """
    data = await state.get_data()
    controller = data.get("controller")

    if controller.target_state == StatisticStates.parametrized_end_period_years:
        possible_error = controller.set_year(year=message.text, edge="end")
        kb = ReplyKeyBoard.create_kb(buttons=controller.year_builder())

    elif controller.target_state == StatisticStates.parametrized_end_period_days:
        possible_error = controller.set_day(
            day=message.text,
            month=controller.end.month,
            year=controller.end.year,
            edge="end",
        )
        kb = ReplyKeyBoard.create_kb(controller.day_builder(date=controller.start))
    else:
        possible_error = controller.set_month(month=message.text, edge="end")
        kb = ReplyKeyBoard.create_kb(buttons=texts["reply_buttons"]["months"])

    if possible_error:
        await state.set_state(StatisticStates.got_dates)
        return await message.answer(text=possible_error, reply_markup=kb)

    start_date, end_date = controller.dates_repr()

    dates_message = texts["statistic_texts"]["group_type"].format(
        start=start_date, end=end_date
    )
    await state.set_state(StatisticStates.waiting_for_group_type)
    return await message.answer(
        text=dates_message,
        reply_markup=InlineKeyBoard.create_kb(
            buttons=texts["inline_buttons"]["statistic"]["group_types"]
        ),
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_group_type), F.data == "period_group_type"
)
async def statistic_period_group_type_handler(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает выбор типа группировки по периоду для формирования отчетности.

    :param callback: CallbackQuery - запрос с выбранным типом группировки.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор типа файла для отчета.
    """
    data = await state.get_data()
    controller = data.get("controller")
    controller.set_group_type(group_type=callback.data)

    await state.set_state(StatisticStates.waiting_for_file_type)

    return await callback.message.answer(
        text=texts["statistic_texts"]["period_group_type"],
        reply_markup=InlineKeyBoard.create_kb(
            buttons=texts["inline_buttons"]["statistic"]["period_group_type"]
        ),
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_group_type), F.data == "article_group_type"
)
async def statistic_article_group_type_handler(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает выбор типа группировки по статьям для формирования отчетности.

    :param callback: CallbackQuery - запрос с выбранным типом группировки.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на выбор типа файла для отчета.
    """
    data = await state.get_data()
    controller = data.get("controller")
    controller.set_group_type(group_type=callback.data)

    await state.set_state(StatisticStates.waiting_for_file_type)
    return await statistic_file_type_handler(callback, state, texts)


@statistic_router.callback_query(StateFilter(StatisticStates.waiting_for_file_type))
async def statistic_file_type_handler(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает выбор типа файла для формирования отчетности.

    :param callback: CallbackQuery - запрос с выбранным типом файла.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет запрос на генерацию отчета.
    """
    data = await state.get_data()
    controller = data.get("controller")
    if controller.group_type != callback.data:
        controller.set_group_type_period(group_type_period=callback.data)

    await state.set_state(StatisticStates.got_all_data)

    return await callback.message.answer(
        text=texts["statistic_texts"]["file_type"],
        reply_markup=InlineKeyBoard.create_kb(
            buttons=texts["inline_buttons"]["file_type"], adjust=3
        ),
    )


@statistic_router.callback_query(StateFilter(StatisticStates.got_all_data))
async def statistic_launch_report_handler(
    callback: CallbackQuery, state: FSMContext, texts: dict
):
    """
    Обрабатывает запуск отчета и отправку документа пользователю.

    :param callback: CallbackQuery - запрос на запуск отчета.
    :param state: FSMContext - состояние конечного автомата для пользователя.
    :param texts: dict - словарь с текстами для сообщений.
    :return: отправляет готовый отчет пользователю.
    """
    data = await state.get_data()
    controller = data.get("controller")
    if not controller.file_type:
        controller.set_file_type(file_type=callback.data)

    file_path = await controller.get_report()
    await state.set_data({})

    return await callback.message.answer_document(
        caption=texts["statistic_texts"]["report_is_done"],
        document=FSInputFile(file_path),
        reply_markup=InlineKeyBoard.create_kb(buttons=texts["inline_buttons"]["ok"]),
    )
