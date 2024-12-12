from aiogram.fsm.state import StatesGroup, State


__all__ = [
    'InsertStates',
    'DeleteStates',
    'LimitsStates',
    'TimezoneStates',
    'StatisticStates'
]


class InsertStates(StatesGroup):
    waiting_for_insert_item = State()
    waiting_for_insert_sum = State()
    waiting_for_repeat_insert = State()


class DeleteStates(StatesGroup):
    waiting_for_chose_article = State()
    waiting_for_delete_article = State()
    waiting_for_repeat_deletion = State()


class LimitsStates(StatesGroup):
    waiting_for_limits_item = State()
    waiting_for_limits_sum = State()
    waiting_for_repeat_limits = State()


class TimezoneStates(StatesGroup):
    waiting_for_add_timezone = State()
    waiting_for_change_timezone = State()


class StatisticStates(StatesGroup):
    waiting_for_report_type = State()

    parametrized_start_period_years = State()
    parametrized_end_period_years = State()

    parametrized_start_period_months = State()
    parametrized_end_period_months = State()

    parametrized_start_period_days = State()
    parametrized_end_period_days = State()

    got_dates = State()

    waiting_for_group_type = State()
    got_all_data = State()
