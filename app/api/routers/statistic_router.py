from copy import deepcopy
from typing import Union

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard
from app.api.servises.fsm.states import StatisticStates
from app.api.servises.kb_builders.reply_kb import ReplyKeyBoard
from app.api.servises.kb_builders.inline_kb import InlineKeyBoard
from app.api.servises.helpers.helpers import year_builder, day_builder, create_correct_dates, validate_data


__all__ = ['statistic_router']

statistic_router = Router()


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_report_type),
    F.data == 'fast_report'
)
async def statistic_make_fast_report(callback: CallbackQuery, state: FSMContext, texts: dict):
    # TODO тут запускаются процессы по формированию быстрого отчета
    # TODO отчет сразу выводится клиенту
    await state.set_data({})
    return await callback.message.answer(
        text='Хуй тебе, а не отчет'
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_report_type),
    F.data == 'parametrized_report'
)
async def statistic_parametrized_report(callback: CallbackQuery, state: FSMContext, texts: dict):
    await state.set_data({})
    await state.set_state(StatisticStates.parametrized_start_period_years)
    return await callback.message.answer(
        text=texts['statistic_texts']['period_type'],
        reply_markup=InlineKeyBoard.create_kb(
            buttons=texts['inline_buttons']['statistic']['period_type'],
            adjust=3
        )
    )


@statistic_router.callback_query(StateFilter(StatisticStates.parametrized_start_period_years))
async def statistic_start_year_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    await state.set_data(
        {
            'target_state': callback.data,
            'dates': deepcopy(texts['dates'])
        }
    )
    target_state = getattr(StatisticStates, callback.data)

    if target_state == StatisticStates.parametrized_end_period_years:
        await state.set_state(StatisticStates.parametrized_end_period_years)
    else:
        await state.set_state(StatisticStates.parametrized_start_period_months)

    return await callback.message.answer(
        text=texts['statistic_texts']['years']['start'],
        reply_markup=ReplyKeyBoard.create_kb(buttons=year_builder())
    )


@statistic_router.message(StateFilter(StatisticStates.parametrized_start_period_months))
async def statistic_start_month_handler(message: Message, state: FSMContext, texts: dict):
    validated_year = validate_data(field='year', value=message.text)
    if isinstance(validated_year, str):
        return await message.answer(
            text=validated_year,
            reply_markup=ReplyKeyBoard.create_kb(buttons=year_builder())
        )
    data = await state.get_data()
    dates = data.get('dates')
    dates['years']['start'] = validated_year.year
    await state.update_data({'dates': dates})
    target_state = getattr(StatisticStates, data['target_state'])

    if target_state == StatisticStates.parametrized_end_period_months:
        await state.set_state(StatisticStates.parametrized_end_period_years)
    else:
        await state.set_state(StatisticStates.parametrized_start_period_days)

    return await message.answer(
        text=texts['statistic_texts']['months']['start'].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
    )


@statistic_router.message(StatisticStates.parametrized_start_period_days)
async def statistic_start_day_handler(message: Message, state: FSMContext, texts: dict):
    validated_month = validate_data(field='month', value=message.text)
    if isinstance(validated_month, str):
        return await message.answer(
            text=validated_month,
            reply_markup=ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
        )
    data = await state.get_data()
    dates = data.get('dates')
    dates['months']['start'] = validated_month.month
    await state.update_data({'dates': dates})

    await state.set_state(StatisticStates.parametrized_end_period_years)

    days_buttons = day_builder(year=dates['years']['start'], month=dates['months']['start'])
    return await message.answer(
        text=texts['statistic_texts']['days']['start'].format(month=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=days_buttons)
    )


@statistic_router.message(StatisticStates.parametrized_end_period_years)
async def statistic_end_year_handler(message: Message, state: FSMContext, texts: dict):
    data = await state.get_data()
    dates = data.get('dates')
    target_state = getattr(StatisticStates, data['target_state'])
    try:
        if target_state == StatisticStates.parametrized_end_period_years:
            validated_data = validate_data(field='year', value=message.text)
            kb = ReplyKeyBoard.create_kb(buttons=year_builder())
            dates['years']['start'] = validated_data.year
            await state.set_state(StatisticStates.got_dates)

        else:
            await state.set_state(StatisticStates.parametrized_end_period_months)
            if target_state == StatisticStates.parametrized_end_period_days:
                validated_data = validate_data(field='day', value=message.text, year=dates['years']['start'], month=dates['months']['start'])
                kb = ReplyKeyBoard.create_kb(
                    day_builder(year=dates['years']['start'], month=dates['months']['start'])
                )
                dates['days']['start'] = validated_data.day

            else:
                validated_data = validate_data(field='month', value=message.text)
                kb = ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
                dates['months']['start'] = validated_data.month
    # TODO Тут и во втором таком же месте придумать, как выдавать соответствующую клавиатуру
    except AttributeError:
        await state.set_state(StatisticStates.parametrized_end_period_years)
        return await message.answer(
            text=validated_data,
            reply_markup=kb
        )

    await state.update_data({'dates': dates})

    return await message.answer(
        text=texts['statistic_texts']['years']['end'].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=year_builder(start_year=dates['years']['start']))
    )


@statistic_router.message(StateFilter(StatisticStates.parametrized_end_period_months))
async def statistic_end_month_handler(message: Message, state: FSMContext, texts: dict):
    validated_year = validate_data(field='year', value=message.text)
    if isinstance(validated_year, str):
        return await message.answer(
            text=validated_year,
            reply_markup=ReplyKeyBoard.create_kb(buttons=year_builder())
        )
    data = await state.get_data()
    dates = data.get('dates')
    target_state = getattr(StatisticStates, data['target_state'])
    dates['years']['end'] = validated_year.year
    await state.update_data({'dates': dates})

    if target_state == StatisticStates.parametrized_end_period_months:
        await state.set_state(StatisticStates.got_dates)
    else:
        await state.set_state(StatisticStates.parametrized_end_period_days)

    return await message.answer(
        text=texts['statistic_texts']['months']['end'].format(year=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
    )


@statistic_router.message(StatisticStates.parametrized_end_period_days)
async def statistic_end_day_handler(message: Message, state: FSMContext, texts: dict):
    validated_month = validate_data(field='month', value=message.text)
    if isinstance(validated_month, str):
        return await message.answer(
            text=validated_month,
            reply_markup=ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
        )
    data = await state.get_data()
    dates = data.get('dates')
    dates['months']['end'] = validated_month.month
    await state.update_data({'dates': dates})

    await state.set_state(StatisticStates.got_dates)

    days_buttons = day_builder(year=dates['years']['start'], month=dates['months']['start'])
    return await message.answer(
        text=texts['statistic_texts']['days']['end'].format(month=message.text),
        reply_markup=ReplyKeyBoard.create_kb(buttons=days_buttons)
    )


@statistic_router.message(StatisticStates.got_dates)
async def statistic_got_dates_handler(message: Message, state: FSMContext, texts: dict):
    data = await state.get_data()
    dates = data.get('dates')
    target_state = getattr(StatisticStates, data['target_state'])

    try:
        if target_state == StatisticStates.parametrized_end_period_years:
            validated_data = validate_data(field='year', value=message.text)
            kb = ReplyKeyBoard.create_kb(buttons=year_builder(start_year=dates['years']['start']))
            dates['years']['end'] = validated_data.year
        elif target_state == StatisticStates.parametrized_end_period_months:
            validated_data = validate_data(field='month', value=message.text)
            kb = ReplyKeyBoard.create_kb(buttons=texts['reply_buttons']['months'])
            dates['months']['end'] = validated_data.month
        else:
            validated_data = validate_data(field='day', value=message.text, year=dates['years']['start'],
                                           month=dates['months']['start'])
            kb = ReplyKeyBoard.create_kb(
                buttons=day_builder(year=dates['years']['start'], month=dates['months']['start'])
            )
            dates['days']['end'] = validated_data.day
    except AttributeError:
        await state.set_state(StatisticStates.got_dates)
        return await message.answer(
            text=validated_data,
            reply_markup=kb
        )

    dates = await state.get_data()
    await state.update_data({'dates': dates})
    start_date, end_date = create_correct_dates(dates=dates.get('dates'))
    dates_message = texts['statistic_texts']['group_type'].format(start=start_date, end=end_date)
    await state.set_state(StatisticStates.waiting_for_group_type)
    return await message.answer(
        text=dates_message,
        reply_markup=InlineKeyBoard.create_kb(buttons=texts['inline_buttons']['statistic']['group_types'])
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_group_type),
    F.data == 'period_group_type'
)
async def statistic_period_group_type_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    # TODO добавить с тжет дата щапись о периоде - какой период выбран для группировки
    await state.set_state(StatisticStates.got_all_data)

    return await callback.message.answer(
        text=texts['statistic_texts']['period_group_type'],
        reply_markup=InlineKeyBoard.create_kb(buttons=texts['inline_buttons']['statistic']['period_group_type'])
    )


@statistic_router.callback_query(
    StateFilter(StatisticStates.waiting_for_group_type),
    F.data == 'article_group_type'
)
async def statistic_article_group_type_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    await state.set_state(StatisticStates.got_all_data)
    return await statistic_launch_report_handler(callback, state, texts)
    # TODO добавить тоже, что юырана группировка по статьям


@statistic_router.callback_query(StateFilter(StatisticStates.got_all_data))
async def statistic_launch_report_handler(callback: CallbackQuery, state: FSMContext, texts: dict):
    # TODO запустить сервис группировки отчетов
    return await callback.message.answer(
        text=texts['statistic_texts']['got_all_parameters'],
        reply_markup=InlineKeyBoard.create_kb(buttons=texts['inline_buttons']['ok'])
    )
