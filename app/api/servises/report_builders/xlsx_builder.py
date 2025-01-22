from typing import LiteralString
import os

import pandas as pd

from app.api.servises.report_builders import BaseBuilder
from app.utils import logged

__all__ = ["XLSXBuilder"]


@logged()
class XLSXBuilder(BaseBuilder):
    def write_data(self, data: dict) -> LiteralString | str | bytes:
        """
        Записывает данные в файл XLSX.

        :param data: dict - словарь с данными для записи, где ключи - периоды,
                     а значения - DataFrame с данными.
        :return: LiteralString | str | bytes - путь к записанному файлу XLSX.
        """
        self.log.debug(f"Метод write_data. Записываем данные в файл XLS.")
        file_path = os.path.join(self.folder, self.filename + ".xlsx")

        with pd.ExcelWriter(file_path) as writer:
            self.log.debug(f"Метод write_data. Открыли врайтер.")

            for period, df in data.items():
                self.log.debug(f"Метод write_data. Смотрим айтемы {period}.")

                df.to_excel(writer, sheet_name=period, index=False, float_format="%.2f")
        self.log.debug(f"Метод write_data. Данные записаны в файл {file_path}.")

        return file_path
