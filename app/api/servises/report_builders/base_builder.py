import os
from abc import abstractmethod

import pandas as pd


__all__ = ['BaseBuilder']


class BaseBuilder:
    def __init__(self, data: dict, tg_id: int):
        self.data = data
        self.data_frame = None
        self.folder = os.path.join('/bot', 'api', 'static', 'temp')
        os.makedirs(self.folder, exist_ok=True)
        self.filename = f'Отчет для пользователя с id {tg_id}'

    def launch(self):
        self.data_frame: pd.DataFrame = pd.DataFrame.from_dict(self.data, orient="index").reset_index()
        self.data_frame.rename(columns={'index': 'Статья расходов'}, inplace=True)
        return self.generate_report()

    @abstractmethod
    def write_data(self):
        pass

    @abstractmethod
    def generate_report(self):
        pass

