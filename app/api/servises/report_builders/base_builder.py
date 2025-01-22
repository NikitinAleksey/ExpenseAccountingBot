import os
from abc import abstractmethod
from typing import LiteralString

import pandas as pd

from app.utils import logged

__all__ = ["BaseBuilder"]


@logged()
class BaseBuilder:
    def __init__(self, expenses: list[tuple], limits: dict, tg_id: int):
        """
        Инициализация класса для создания отчета.

        :param expenses: list[tuple] - список расходов в виде кортежей (период, сумма, категория).
        :param limits: dict - словарь лимитов по категориям.
        :param tg_id: int - ID пользователя в Telegram.
        """
        self.expenses = expenses
        self.limits = limits
        self.data_frame = None
        self.folder = os.path.join("/bot", "api", "static", "temp")
        os.makedirs(self.folder, exist_ok=True)
        self.filename = f"Отчет для пользователя с id {tg_id}"

    def generate_report(self):
        """
        Генерирует отчет по расходам для пользователя.

        :return: str - путь к файлу с отчетом.
        """
        self.log.debug(f"Метод generate_report. Подготовка данных.")
        periods = sorted(set([expense[0] for expense in self.expenses]))
        tables_by_period = {}

        for period in periods:
            period_expenses = [
                expense for expense in self.expenses if expense[0] == period
            ]

            df = pd.DataFrame(period_expenses, columns=["period", "summ", "category"])
            df = df.groupby("category", as_index=False).agg({"summ": "sum"})
            df["limit"] = df["category"].map(self.limits)

            df = df[["category", "summ", "limit"]]
            df = df.rename(
                columns={
                    "category": "Название статьи расходов",
                    "summ": "Сумма трат",
                    "limit": "Лимит",
                }
            )
            df["Процент расхода"] = (
                ((df["Сумма трат"] / df["Лимит"]) * 100).round(0).astype(int)
            )

            tables_by_period[period] = df
        self.log.debug(f"Метод generate_report. Данные подготовлены.")

        return self.write_data(data=tables_by_period)

    @abstractmethod
    def write_data(self, data: dict) -> LiteralString | str | bytes:
        """
        Абстрактный метод для записи данных отчета.

        :param data: dict - словарь с данными по периодам и расходам.
        :return: None
        """
        pass
